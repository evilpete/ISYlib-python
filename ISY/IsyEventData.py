"""
This is a data file for IsyEvent.py

"""
# author : Peter Shipley <peter.shipley@gmail.com>
# copyrigh :  Copyright (C) 2017 Peter Shipley
# license : BSD


__all__ = [] # EVENT_CTRL, LOG_USERID

    ## EVENT_CTRL ##

EVENT_CTRL = {
    "_0" : "Heartbeat",
    "_1" : "Trigger",
    "_2" : "Protocol Specific",
    "_3" : "Nodes Updated",
    "_4" : "System Config Updated",
    "_5" : "System Status",
    "_6" : "Internet Access",
    "_7" : "System Progress",
    "_8" : "Security System",
    "_9" : "System Alert",
    "_10" : "OpenADR", #"Electricity",
    "_11" : "Climate",
    "_12" : "AMI/SEP",
    "_13" : "Ext Energy Mon",
    "_14" : "UPB Linker",
    "_15" : "UPB Dev State",
    "_16" : "UPB Dev Status",
    "_17" : "Gas",
    "_18" : "ZigBee",
    "_19" : "Elk",
    "_20" : "Device Link",
    "_21" : "Z-Wave",
    "_22" : "Billing",
    "_23" : "Portal",
    "DON" : "Device On",
    "DFON" : "Device Fast On",
    "DOF" : "Device Off",
    "DFOF" : "Device Fast Off",
    "ST" : "Status",
    "OL" : "On Level",
    "RR" : "Ramp Rate",
    "BMAN" : "Start Manual Change",
    "SMAN" : "Stop Manual Change",
    "CLISP" : "Setpoint",
    "CLISPH" : "Heat Setpoint",
    "CLISPC" : "Cool Setpoint",
    "CLIFS" : "Fan State",
    "CLIMD" : "Thermostat Mode",
    "CLIHUM" : "Humidity",
    "CLIHCS" : "Heat/Cool State",
    "BRT" : "Brighten",
    "DIM" : "Dim",
    "X10" : "Direct X10 Commands",
    "BEEP" : "Beep",
    }

EVENT_CTRL_ACTION = {
    "_0" : { },

    "_1" : {
        '0': "Event Status",
        '1': "Get Status",
        '2': "Key Change",
        '3': "Info String",
        '4': "IR Learn Mode",
        '5': "Schedule",
        '6': "Var Stat",
        '7': "Var Init",
        '8': "Key",
        },

    # Driver Specific Events
    "_2" : {},

    # Node Changed/Updated
    '_3': {
        'NN': 'Node Renamed',
        'NR': 'Node Removed',
        'ND': 'Node Added',
        'MV': 'Node Moved (into a scene)',
        'CL': 'Link Changed (in a scene)',
        'RG': 'Removed From Group (scene)',
        'EN': 'Enabled',
        'PC': 'Parent Changed',
        'PI': 'Power Info Changed',
        'DI': 'Device ID Changed',
        'DP': 'Device Property Changed',
        'GN': 'Group Renamed',
        'GR': 'Group Removed',
        'GD': 'Group Added',
        'FN': 'Folder Renamed',
        'FR': 'Folder Removed',
        'FD': 'Folder Added',
        'NE': 'Node Error (Comm. Errors)',
        'CE': 'Clear Node Error (Comm. Errors Cleared)',
        'SN': 'Discovering Nodes (Linking)',
        'SC': 'Node Discovery Complete',
        'WR': 'Network Renamed',
        'WH': 'Pending Device Operation',
        'WD': 'Programming Device',
        'RV': 'Node Revised (UPB)',
        },

    # System Configuration Updated
    '_4': {
        '0': 'Time Changed',
        '1': 'Time Configuration Changed',
        '2': 'NTP Settings Updated',
        '3': 'Notifications Settings Updated',
        '4': 'NTP Communications Error',
        '5': 'Batch Mode Updated',
        '6': 'Battery Mode Programming Updated',
        },

    # System Status Updated
    '_5': {
        '0': 'Not Busy',
        '1': 'Busy',
        '2': 'Idle',
        '3': 'Safe Mode',
        },

    # Internet Access Status
    '_6': {
        '0': 'Disabled',
        '1': 'Enabled',
        '2': 'Failed',
        },

    # Progress Report
    '_7': {
        '1': 'Update',
        '2.1': 'Device Adder Info (UPB Only)',
        '2.2': 'Device Adder Warn (UPB Only)',
        '2.3': 'Device Adder Error (UPB Only)',
        },

    # Security System Event
    '_8': {
        '0': 'Disconnected',
        '1': 'Connected',
        'DA': 'Disarmed',
        'AW': 'Armed Away',
        'AS': 'Armed Stay',
        'ASI': 'Armed Stay Instant',
        'AN': 'Armed Night',
        'ANI': 'Armed Night Instant',
        'AV': 'Armed Vacation',
        },

    # System Alert Event
    "_9" : {},

    # Electricity / OpenADR and Flex Your Power Events
    '_10': {
        '1': 'Open ADR Error',
        '2': 'Open ADR Status Update',
        '5': 'Flex Your Power Error',
        '6': 'Flex Your Power Status Updated',
        '8': 'OpenADR Registration Status',
        '9': 'OpenADR Report Status',
        '10': 'OpenADR Opt Status',
        },


    # Climate Events
    '_11': {
        '0': 'Error',
        '1': 'Temperature',
        '2': 'Temperature High',
        '3': 'Temperature Low',
        '4': 'Feels Like',
        '5': 'Temperature Rate',
        '6': 'Humidity',
        '7': 'Humidity Rate',
        '8': 'Pressure',
        '9': 'Pressure Rate',
        '10': 'Dew Point',
        '11': 'Wind Speed',
        '12': 'Average Wind Speed',
        '13': 'Wind Direction',
        '14': 'Average Wind Direction',
        '15': 'Gust Wind Speed',
        '16': 'Gust Wind Direction',
        '17': 'Rain Today',
        '18': 'Ambient Light',
        '19': 'Light Rate',
        '20': 'Rain Rate',
        '21': 'Rain Rate Max',
        '22': 'Evapotranspiration',
        '23': 'Irrigation Requirement',
        '24': 'Water Deficit Yesterday',
        '25': 'Elevation',
        '26': 'Coverage',
        '27': 'Intensity',
        '28': 'Weather Condition',
        '29': 'Cloud Condition',
        '30': "Tomorrow's Forecast: Average Temperature",
        '31': "Tomorrow's Forecast: High Temperature",
        '32': "Tomorrow's Forecast: Low Temperature",
        '33': "Tomorrow's Forecast: Humidity",
        '34': "Tomorrow's Forecast: Wind Speed",
        '35': "Tomorrow's Forecast: Gust Speed",
        '36': "Tomorrow's Forecast: Rain",
        '37': "Tomorrow's Forecast: Snow",
        '38': "Tomorrow's Forecast: Coverage",
        '39': "Tomorrow's Forecast: Intensity",
        '40': "Tomorrow's Forecast: Weather Condition",
        '41': "Tomorrow's Forecast: Cloud Condition",
        '42': '24 Hour Forecast: Average Temperature',
        '43': '24 Hour Forecast: High Temperature',
        '44': '24 Hour Forecast: Low Temperature',
        '45': '24 Hour Forecast: Humidity',
        '46': '24 Hour Forecast: Rain',
        '47': '24 Hour Forecast: Snow',
        '48': '24 Hour Forecast: Coverage',
        '49': '24 Hour Forecast: Intensity',
        '50': '24 Hour Forecast: Weather Condition',
        '51': '24 Hour Forecast: Cloud Condition',
        '100': 'Last Updated Timestamp',
        },

    # ISY SEP EVENTS
    '_12': {
        '1': 'Network Status Changed',
        '2': 'Time Status Changed',
        '3': 'New Message',
        '4': 'Message Stopped',
        '5': 'New Price',
        '6': 'Price Stopped',
        '7': 'New DR Event',
        '8': 'DR Event Stopped',
        '9': 'Metering Event',
        '10': 'Metering Format Event',
        '31': 'Scheduled Message',
        '51': 'Scheduled Price',
        '71': 'Scheduled DR Event',
        '110': 'Fast Poll Mode',
        '111': 'Normal Poll Mode',
        },

    # External Energy Monitoring Events
    '_13': {
        '1': 'Number of Channels',
        '2': 'Channel Report',
        '3': 'Zigbee Status',
        '7': 'Raw Packet',
        },

    # UPB Linker Events
    '_14': {
        '1': 'Device Status',
        '2': 'Pending Stop Find',
        '3': 'Pending Cancel Device Adder',
        },

    # UPB Dev State
    '_15': {},

    # UPB Device Status Events
    '_16': {
        '1': 'Device Signal Report',
        '2': 'Device Signal Report Removed',
        },

    # Gas Meter Events
    '_17': {
        '1': 'Status',
        '2': 'Error',
        },

    # Zigbee Events
    '_18': {
        '1': 'Status',
        },

    # ELK
    "_19" : {},

    # Device Linker Events
    '_20': {
        '1': 'Status',
        '2': 'Cleared',
        },

    # Z-Wave
    "_21" : {},

    # Billing Events
    '_22': {
        '1': 'Cost/Usage Changed Event',
        },

    # Portal Events
    '_23': {
        '1': 'Status',
        },

}

LOG_USERID = [ "SYSTEM_USER", "SYSTEM_DRIVER_USER", "WEB_USER",
            "SCHEDULER_USER", "D2D_USER", " ELK_USER",
            "SEP_DEVICE_UMETER_USER", "SEP_DEVICE_UPRICE_USER",
            "SEP_DEVICE_UMSG_USER", "SEP_DEVICE_UDR_USER",
            "GAS_METER_USER" ]


LOG_TYPES = {
    "1": "SYSTEM_STARTUP",
    "2": "SYSTEM_SHUTDOWN",
    "3": "WARNING",
    "4": "INFO",
    "5": "LOG",
    "6": "UD_SEP_SUBSYS_STARTUP",
    "-1": "REQUEST_FAILED_ERROR",
    "-2": "DEVICE_COMMUNICATION_ERROR",
    "-3": "DEVICE_RETURNED_INVALID_NODE",
    "-4": "DEVICE_RETURNED_INVALID_ADDRESS",
    "-5": "ERROR_LOGGER_STARTUP",
    "-10": "MAIN_HAML_DRIVER_NOT_FOUND",
    "-20": "MAIN_LOCAL_DEVICE_BLANK",
    "-100": "SYSTEM_NO_NETWORK_CONNECTION",
    "-101": "SYSTEM_WEBSERVER_SELECT_FAILED",
    "-500": "HAML_DRIVER_LISTENER_NOT_REGISTERED",
    "-1000": "HAML_PARSER_UNDEFINED_ELEMENT",
    "-1001": "HAML_PARSER_ONDATA",
    "-5001": "UPNP_DRIVER_NO_DEVICES_CONFIGURED",
    "-5002": "UPNP_DRIVER_SERIAL_READER_FAILED",
    "-5003": "UPNP_DRIVER_MAX_DEVICES",
    "-5004": "UPNP_SERVICE_TYPE_SEARCH_NS",
    "-5005": "UPNP_SUBSCRIPTION_NOT_FOUND_FOR_RENEWAL",
    "-5006": "UPNP_SUBSCRIPTION_NOT_FOUND_FOR_CANCELATION",
    "-5007": "UPNP_INVALID_SUBSCRIPTION_URL",
    "-5008": "UPNP_INVALID_SUBSCRIPTION_CALLBACK",
    "-5009": "UPNP_MAX_SUBSCRIBERS",
    "-5010": "UPNP_SUBSCRIBER_TCP_CONNECT_FAILURE",
    "-5011": "PROCESS_DEVICE_STATE_CHANGE_SID_NOT_FOUND",
    "-5012": "UPNP_SUBSCRIBER_NOREPLY_TO_EVENT_1",
    "-5013": "UPNP_SUBSCRIBER_NOREPLY_TO_EVENT_2",
    "-5014": "UPNP_SUBSCRIBER_NOREPLY_TO_EVENT_3",
    "-5015": "UPNP_CONTROL_MALFORMED_SOAP_REQUEST_1",
    "-5016": "UPNP_CONTROL_MALFORMED_SOAP_REQUEST_2",
    "-6000": "OS_DUPLICATE_TASK_PRIORITY",
    "-6001": "OS_OPEN_SERIAL_FAILED",
    "-7020": "D2D_PARSER_ERROR",
    "-7029": "NOTIFICATIONS_MAIL_TO_ADDRESS_REQUIRED",
    "-7030": "NOTIFICATIONS_SEND_MAIL_FAILED",
    "-7050": "D2D_EXPECTED_D2D_TAG",
    "-7051": "D2D_UNEXPECTED_TAG_IN_SENSE",
    "-7052": "D2D_UNEXPECTED_TAG_IN_CONDITION",
    "-7501": "DIAG_PARSER_ERROR",
    "-7601": "LINK_PARSER_ERROR",
    "-10100": "PNP_SECURITY_NOT_VERIFIED",
    "-10001": "SSL_DECODING_LENGTHS_FAILED",
    "-10002": "SSL_DECODING_PMOD_FAILED",
    "-10003": "SSL_DECODING_PEXP_FAILED",
    "-10004": "SSL_DECODING_PRI_EXP_FAILED",
    "-10005": "SSL_DECODING_PRI_P_FAILED",
    "-10006": "SSL_DECODING_PRI_Q_FAILED",
    "-10007": "SSL_DECODING_PRI_X1_FAILED",
    "-10008": "SSL_DECODING_PRI_X2_FAILED",
    "-10009": "SSL_DECODING_COEFF_FAILED",
    "-10010": "SSL_DECODING_CERT_FAILED",
    "-10011": "SSL_REQUEST_NOT_AUTHENTICATED",
    "-10026": "SECURE_SESSION_DOES_NOT_EXIST",
    "-10027": "SECURE_SESSIONS_EXHAUSTED",
    "-10101": "AUTHENTICATION_UNSUPPORTED_UID_LEN",
    "-10102": "AUTHENTICATION_UNSUPPORTED_PWD_LEN",
    "-10103": "AUTHENTICATION_USER_ID_DOES_NOT_EXIST",
    "-10104": "AUTHENTICATION_USER_ID_PWD_NOT_PRESENT",
    "-10105": "AUTHENTICATION_WRONG_PASSWORD",
    "-10106": "AUTHENTICATION_FAILED",
    "-10107": "HTTP_AUTH_DECODING_FAILED",
    "-11000": "SECURITY_INITIALIZATION_FAILED",
    "-12000": "TIMED_OUT_WAITING_FOR_CRITICAL_SECION",
    "-12001": "ERROR_LEAVING_CRITICAL_SECTION_NOT_OWNED",
    "-13000": "CONTENT_LEN_NOT_EQUAL_TO_HEADER_CONTENT_LEN",
    "-14001 ": "XML_MALFORMED_TAG",
    "-14002": "XML_MALFORMED_END_TAG",
    "-14003 ": "XML_NO_START_TAG",
    "-14004 ": "XML_NO_TAG_NAME",
    "-14005 ": "XML_START_END_NAME_MISMATCH",
    "-20000": "MALFORMED_UPNP_HEADERS",
    "-50000": "MAIL_SERVER_CONNECT_ERROR",
    "-50001": "SMTP_SERVER_FAILURE",
    "-50010": "MAIL_SERVER_DNS_ERROR",
    "-50011": "MAIL_MAX_FROM_LEN",
    "-50012": "MAIL_MAX_SUBJECT_LEN",
    "-50013": "MAIL_MAX_TO_LEN",
    "-60000": "NTP_CONFIG_SERVER_NO_HOST_PARAM",
    "-60001": "NTP_CONFIG_SERVER_ADDRESS_RESOLUTION_FAILED",
    "-60002": "NTP_CONFIG_SERVER_NO_INTERVAL_PARAM",
    "-60006": "NTP_SERVER_NOT_RESPONDING",
    "-60007": "NTP_SERVER_CONNECT_ERROR",
    "-70000": "OUT_OF_MEMORY",
    "-80000": "IGD_FAILED_PARSING_DESCRIPTION_URL",
    "-80001": "IGD_FAILED_RETRIEVING_DESCRIPTION_FILE",
    "-80002": "IGD_FAILED_RETRIEVING_URL_BASE",
    "-80003": "IGD_FAILED_PARSING_URL_BASE",
    "-80004": "IGD_FAILED_RETRIEVING_WAN_CONNECTION_DEVICE",
    "-80005": "IGD_FAILED_RETRIEVING_CONTROL_URL",
    "-80006": "IGD_FAILED_PARSING_CONTROL_URL",
    "-80007": "IGD_FAILED_RETRIEVING_EXTERNAL_IP",
    "-80008": "IGD_NO_RESPONSE_FROM_GATEWAY",
    "-80009": "IGD_FAILED_STRIPPING_HTTP_HEADERS",
    "-80010": "IGD_FAILED_DELETING_PORT_FORWARD_MAP",
    "-80011": "IGD_FAILED_ADDING_PORT_FORWARD_MAP",
    "-80012": "IGD_FAILED_GETTING_SPECIFIC_ENTRY",
    "-90001": "CRC_INVALID_ORDER",
    "-90002": "CRC_INVALID_POLYNOM",
    "-90003": "CRC_INVALID_CRC_INIT",
    "-90004": "CRC_INVALID_CRC_XOR",
    "-100000": "LOGGER_DIRECTORY_CREATION_FAILED",
    "-100001": "LOGGER_SD_IS_NOT_INSTALLED",
    "-100002": "LOGGER_LOG_FILE_OPEN_FAILED",
    "-110000": "FILE_TO_STRING_OPEN_FAILED",
    "-110001": "FILE_TO_STRING_MEM_ALLOC_FAILED",
    "-110002": "SD_DRIVE_FORMAT_FAILED_1",
    "-110003": "SD_DRIVE_FORMAT_FAILED_2",
    "-110004": "SD_DRIVE_MOUNT_FAILED_1",
    "-110005": "SD_DRIVE_MOUNT_FAILED_2",
    "-110006": "SEND_FILE_OPEN_FAILED",
    "-110007": "SEND_FILE_READ_FAILED",
    "-110008": "RECEIVE_FILE_WRITE_FAILED",
    "-110009": "RECEIVE_FILE_OPEN_FAILED",
    "-110010": "SD_DRIVE_DIRECTORY_CREATION_FAILED",
    "-110011": "SD_DRIVE_CONFIG_FILE_OPEN_WRITE_FAILED",
    "-110012": "SD_DRIVE_CONFIG_FILE_OPEN_READ_FAILED",
    "-110013": "SD_DRIVE_CONFIG_WRITE_FAILED",
    "-110014": "SD_DRIVE_CONFIG_READ_FAILED",
    "-110015": "STRING_TO_FILE_OPEN_FAILED",
    "-110016": "STRING_TO_FILE_WRITE_FAILED",
    "-110017": "FILE_TO_STRING_READ_FAILED",
    "-110018": "REMOVE_FILE_FAILED",
    "-110019": "REMOVE_DIR_FAILED",
    "-110020": "FLUSH_FILE_FAILED",
    "-110021": "CLOSE_FILE_FAILED",
    "-110022": "OPEN_FILE_FAILED",
    "-110023": "FLUSH_FILE_SYSTEM_FAILED",
    "-110024": "FILESYSTEM_INIT_FAILED",
    "-110025": "FILESYSTEM_CRIT_FAILED",
    "-120000": "FIRMWARE_UPDATE_OPEN_FILE_FAILED",
    "-120001": "FIRMWARE_UPDATE_HEADER_READ_FAILED",
    "-120002": "FIRMWARE_UPDATE_CHECKSUM_FAILED",
    "-120003": "FIRMWARE_UPDATE_MALLOC_FAILED",
    "-120004": "FIRMWARE_UPDATE_DATA_READ_FAILED",
    "-130000": "ELK_CONFIG_PARSER_ERROR",
    "-140000": "HTTP_CLIENT_DNS_ERROR",
    "-140001": "HTTP_CLIENT_BASE64_ENCRYPTION_FAILED",
    "-140002": "HTTP_CLIENT_CONNECTION_TIMED_OUT",
    "-140003": "HTTP_CLIENT_WRITE_HEADER_FAILED",
    "-140004": "HTTP_CLIENT_WRITE_BODY_FAILED",
    "-140005": "HTTP_CLIENT_READ_RESPONSE_FAILED",
    "-140006": "HTTP_CLIENT_HEADER_NO_STATUS",
    "-140007": "HTTP_CLIENT_RESOURCE_MOVED",
    "-140008": "HTTP_CLIENT_REQUEST_FAILED",
    "-140009": "HTTP_CLIENT_NO_NETWORK",
    "-150000": "TCP_CLIENT_WRITE_FAILED",
    "-150100": "UDP_CLIENT_DNS_ERROR",
    "-160000": "PROTOCOL_READER_READ_ERROR",
    "-160001": "PROTOCOL_READER_BUFFER_OVERFLOW",
    "-160002": "PROTOCOL_READER_REOPEN_ERROR",
    "-170000": "WEB_MODULE_NO_FREE_SPACE",
    "-170001": "SYSTEM_ACCESS_LOG",
    "-180000": "SEP_NETWORK_SCAN_ERROR",
    "-180001": "SEP_NETWORK_KEY_EST_ERROR",
    "-180002": "SEP_NETWORK_DISCOVERY_ERROR",
    "-180003": "SEP_NETWORK_SYNCH_ERROR",
    "-180004": "SEP_MODULE_RESET_ERROR",
    "-180005": "SEP_MODULE_INVALID_CALL_ERROR",
    "-180006": "SEP_MODULE_UNKNOWN_ERROR",
    "-190001": "UDERR_ISY_API_NO_SPACE",
    "-190002": "UDERR_ISY_API_INVALID_8_3_FILENAME",
    "-190003": "UDERR_ISY_API_INVALID_PGM_FILENAME",
    "-190004": "UDERR_ISY_API_INCORRECT_PGM_KEY",
    "-190005": "UDERR_ISY_API_INVALID_PGM_URL_SEARCH_STRING",
    "-200000": "DEVICE_DRIVER_ERROR_MSG",
    "-210001": "CALL_HOME_PORTAL_NO_FD",
}



#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
