'''

Finance Python Gateway Client

@author Dilanka Gamage

'''

from collections import namedtuple
from enum import Enum

import datetime
import hashlib
import hmac
import json
import requests
import uuid

#============================== Gateway Enums ==================================

class ApiVersion(Enum):
    v2_10_0 = "v2_10_0"

class ActionType(Enum):
    # Registry
    PEOPLE_PROFILE = "PEOPLE_PROFILE"
    DRIVER_PROFILE = "DRIVER_PROFILE"
    TAXI_PROFILE = "TAXI_PROFILE"
    TAXI_DRIVER_MAPPING = "TAXI_DRIVER_MAPPING"
    VEHICLE_MODEL_PROFILE = "VEHICLE_MODEL_PROFILE"

    # Transaction
    DRIVER_TRIP_TRANSACTION = "DRIVER_TRIP_TRANSACTION"
    DRIVER_TRIP_SUMMARY = "DRIVER_TRIP_SUMMARY"
    DRIVER_RECENT_TRIP_SUMMARY = "DRIVER_RECENT_TRIP_SUMMARY"
    DRIVER_BLOCK_REASON = "DRIVER_BLOCK_REASON"
    DRIVER_CANCEL_REASON = "DRIVER_CANCEL_REASON"
    DRIVER_CREDIT_DEBIT = "DRIVER_CREDIT_DEBIT"

class DateType(Enum):
    CREATE_TIME = "CREATE_TIME"
    CREATE_DATE = "CREATE_DATE"

class TransactionType(Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class HttpHeader(Enum):
    HMAC = "HMAC"
    AUTH = "AUTH"
    CSRF = "CSRF"

#============================== Gateway Utils ==================================

def json_object_hook(rawJson):
    return namedtuple('Class', rawJson.keys())(*rawJson.values())

def json_to_object(rawJson):
    return json.loads(rawJson, object_hook=json_object_hook)

def generate_hmac(secretKey, rawJson):
    return hmac.new(
                    key=secretKey.encode('utf-8'),
                    msg=rawJson.encode('utf-8'),
                    digestmod=hashlib.sha256
                    ).hexdigest()

def post_http_request(httpUrl, httpBody, hmac):
    print("Http url: " + httpUrl)
    print("Http header: HMAC: " + hmac)
    print("Http body: " + httpBody)
    httpHeaders = {
        'Content-Type': 'application/json',
        HttpHeader.HMAC.value: hmac
    }    
    httpResponse = requests.post(httpUrl, data=httpBody, headers=httpHeaders)
    print("Http response: " + httpResponse.text)
    return httpResponse.text

#============================== Gateway Components =============================

class ClientConfig:
    def __init__(self, serviceEndpoint, hmacSecret, authToken, csrfToken):
        self.serviceEndpoint = serviceEndpoint
        self.hmacSecret = hmacSecret
        self.authToken = authToken
        self.csrfToken = csrfToken

class Sorter:
    def __init__(self, field, DESC):
        self.field = field
        self.DESC = DESC

#============================== Gateway Requests ===============================

class Serializer:
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class GatewayRequest(Serializer):
    def __init__(self, actionType, requestData):
        self.apiVersion = ApiVersion.v2_10_0.value
        self.messageId = str(uuid.uuid4())
        self.requestDate = datetime.datetime.now().isoformat()
        self.validateOnly = False
        self.actionType = actionType.value
        self.requestData = requestData

class BaseReportRequest(Serializer):
    def __init__(self):
        self.fromStaff = False
        self.fromPortal = False
        self.pagingEnabled = True
        self.pageSize = 10
        self.pageIndex = 0
        self.exportEnabled = False
        self.sorters = []

class PeopleProfileReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.peopleId = None
        self.withDriverTripSummary = False
        self.withoutEmptyDriverTripSummary = False

class TaxiProfileReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.taxiId = None

class VehicleModelProfileReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.modelId = None

class DriverProfileReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.driverId = None
        self.withDriverTripSummary = False
        self.withoutEmptyDriverTripSummary = False

class DriverTripTransactionReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.transactionId = None
        self.driverId = None
        self.tripId = None
        self.transactionTypes = []
        self.transactionCategories = []
        self.minAmountInRupee = None
        self.maxAmountInRupee = None
        self.minAmountInCents = None
        self.maxAmountInCents = None
        self.description = None
        self.dateType = DateType.CREATE_TIME.value
        self.fromDate = None
        self.toDate = None
        self.createdBy = None
        self.withDriverProfile = False
 
class DriverTripSummaryReportRequest(DriverTripTransactionReportRequest):
    def __init__(self):
        DriverTripTransactionReportRequest.__init__(self)

class DriverBlockReasonSummaryReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.driverId = None

class DriverCancelReasonProfileReportRequest(BaseReportRequest):
    def __init__(self):
        BaseReportRequest.__init__(self)
        self.reasonId = None

class DriverCreditDebitReportRequest(DriverTripTransactionReportRequest):
    def __init__(self):
        DriverTripTransactionReportRequest.__init__(self)
        self.withTaxiDriverMapping = false

#============================== Gateway Helpers ================================

def process_gateway_request(clientConfig, gatewayRequest):
    rawRequest = gatewayRequest.to_json()
    hmac = generate_hmac(clientConfig.hmacSecret, rawRequest)
    rawResponse = post_http_request(clientConfig.serviceEndpoint, rawRequest, hmac)
    return json_to_object(rawResponse)

def fetch_people_profile(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.PEOPLE_PROFILE, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_profile(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_PROFILE, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_taxi_profile(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.TAXI_PROFILE, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_taxi_driver_mapping(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.TAXI_DRIVER_MAPPING, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_vehicle_model_profile(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.VEHICLE_MODEL_PROFILE, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_trip_transaction(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_TRIP_TRANSACTION, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_trip_summary(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_TRIP_SUMMARY, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_recent_trip_summary(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_RECENT_TRIP_SUMMARY, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_block_reason(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_BLOCK_REASON, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_cancel_reason(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_CANCEL_REASON, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

def fetch_driver_credit_debit(clientConfig, reportRequest):
    gatewayRequest = GatewayRequest(ActionType.DRIVER_CREDIT_DEBIT, reportRequest)
    gatewayResponse = process_gateway_request(clientConfig, gatewayRequest)
    return gatewayResponse.responseData

#============================== Unit Tests =====================================

# The following method will return the client config for UAT environment
def build_uat_client_config():
    return ClientConfig("http://146.148.110.253:8080/proxy/finance/reporting",      # set service endpoint
                        "keep-this-secret",                                         # set hmac secret
                        None,                                                       # set auth token
                        None                                                        # set csrf token
                        )

# The following method will return the client config for Staging environment
def build_stage_client_config():
    return ClientConfig("https://finance-report.picme.lk/proxy/finance/reporting", # set service endpoint
                        "vLt0kDgoDsvaahy0mKhzY8OWFYHZqAmM",                        # set hmac secret
                        None,                                                      # set auth token
                        None                                                       # set csrf token
                        )

# The following method will return the client config for Production environment
def build_prod_client_config():
    return ClientConfig("https://finance-report.pickme.lk/proxy/finance/reporting", # set service endpoint
                        "vLt0kDgoDsvaahy0mKhzY8OWFYHZqAmM",                        # set hmac secret
                        None,                                                      # set auth token
                        None                                                       # set csrf token
                        )

# Init client config, common for all tests
clientConfig = build_uat_client_config()
#clientConfig = build_stage_client_config()
#clientConfig = build_prod_client_config()

# The following test will fetch People profile(s) with trip summaries
def test_fetch_people_profile():
    # Build report request
    # NOTE: PeopleProfileReportRequest is a subclass of BaseReportRequest.
    #       Therefore, the BaseReportRequest's state can be altered via PeopleProfileReportRequest, as well.
    reportRequest = PeopleProfileReportRequest()
    # Set request params
    #reportRequest.peopleId = 223 # fetch an individual profile
    reportRequest.withDriverTripSummary = True # fetch with driver trip summary
    reportRequest.withoutEmptyDriverTripSummary = False # fetch with out empty driver trip summary
    # Apply sorters
    sortByPeopleIdDesc = Sorter("peopleId", True)
    reportRequest.sorters.append(sortByPeopleIdDesc)
    # Call report
    reportResponse = fetch_people_profile(clientConfig, reportRequest)
    # Process report response
    if (len(reportResponse.profiles) == 0):
        print("No people profile fetched !!!");
        return
    for profile in reportResponse.profiles:
        print(str(profile))
        
# The following test will fetch Driver profile(s) with trip summaries
def test_fetch_driver_profile():
    # Build report request
    # NOTE: DriverProfileReportRequest is a subclass of BaseReportRequest.
    #       Therefore, the BaseReportRequest's state can be altered via DriverProfileReportRequest, as well.
    reportRequest = DriverProfileReportRequest()
    # Set request params
    #reportRequest.driverId = 223 # fetch an individual profile
    reportRequest.withDriverTripSummary = True # fetch with driver trip summary
    reportRequest.withoutEmptyDriverTripSummary = False # fetch with out empty driver trip summary
    # Apply sorters
    sortByDriverIdDesc = Sorter("driverId", True)
    reportRequest.sorters.append(sortByDriverIdDesc)
    # Call report
    reportResponse = fetch_driver_profile(clientConfig, reportRequest)
    # Process report response
    if (len(reportResponse.profiles) == 0):
        print("No driver profile fetched !!!");
        return
    for profile in reportResponse.profiles:
        print(str(profile))

# The following test will fetch Driver trip transaction(s)
def test_fetch_driver_trip_transaction():
    # Build report request
    # NOTE: DriverTripTransactionReportRequest is a subclass of BaseReportRequest.
    #       Therefore, the BaseReportRequest's state can be altered via DriverProfileReportRequest, as well.
    reportRequest = DriverTripTransactionReportRequest()
    # Set request params
    #reportRequest.transactionId = 20060799 # fetch an individual transaction id
    reportRequest.driverId = 223 # fetch by driver id
    #reportRequest.tripId = 382818176 # fetch by trip id
    # Apply date range filters
    #reportRequest.dateType = DateType.CREATE_TIME.value # mandatory to set date type
    reportRequest.fromDate = "2019-01-01" # in yyyy-MM-dd'T'HH:mm:ss.SSSZ and yyyy-MM-dd HH:mm:ss as well
    reportRequest.toDate = "2019-12-31" # in yyyy-MM-dd'T'HH:mm:ss.SSSZ and yyyy-MM-dd HH:mm:ss as well
    # Apply min and max amount filters
    #reportRequest.minAmountInCents = 199 
    #reportRequest.maxAmountInCents = 9999
    reportRequest.withDriverProfile = True # fetch with driver profile
    # Apply sorters
    sortByTransactionIdDesc = Sorter("transactionId", True)
    reportRequest.sorters.append(sortByTransactionIdDesc)
    # Call report
    reportResponse = fetch_driver_trip_transaction(clientConfig, reportRequest)
    # Process report response
    if (len(reportResponse.transactions) == 0):
        print("No driver trip transaction fetched !!!");
        return
    for transaction in reportResponse.transactions:
        print(str(transaction))

# The following test will fetch Driver trip summary(ies)
def test_fetch_driver_trip_summary():
    # Build report request
    # NOTE: DriverTripSummaryReportRequest is a subclass of BaseReportRequest and DriverTripTransactionReportRequest.
    #       Therefore, the BaseReportRequest's state can be altered via DriverTripSummaryReportRequest, as well.
    reportRequest = DriverTripSummaryReportRequest()
    reportRequest.driverId = 223 # fetch by driver id (mandatory to set)
    # Call report
    reportResponse = fetch_driver_trip_summary(clientConfig, reportRequest)
    # Process report response
    if (len(reportResponse.summaries) == 0):
        print("No driver trip summary fetched !!!");
        return
    for summary in reportResponse.summaries:
        print(str(summary))

# The following test will fetch Driver block reason(s)
def test_fetch_driver_block_reason():
    # Build report request
    # NOTE: DriverBlockReasonSummaryReportRequest is a subclass of BaseReportRequest.
    #       Therefore, the BaseReportRequest's state can be altered via DriverBlockReasonSummaryReportRequest, as well.
    reportRequest = DriverBlockReasonSummaryReportRequest()
    reportRequest.driverId = 223 # fetch by driver id (mandatory to set)
    # Call report
    reportResponse = fetch_driver_block_reason(clientConfig, reportRequest)
    # Process report response
    if (len(reportResponse.summaries) == 0):
        print("No driver trip summary fetched !!!");
        return
    for summary in reportResponse.summaries:
        print(str(summary))

# Run unit tests
#print("\n#################### Test test_fetch_people_profile #################")
#test_fetch_people_profile()
print("\n#################### Test test_fetch_driver_profile #################")
#test_fetch_driver_profile()
#print("\n#################### Test test_fetch_driver_trip_transaction ########")
test_fetch_driver_trip_transaction()
print("\n#################### Test test_fetch_driver_trip_summary ############")
test_fetch_driver_trip_summary()