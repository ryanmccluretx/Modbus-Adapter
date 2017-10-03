"""modbus-client-adapter"""
import sys
import argparse
import logging
import os
import json
from clearblade.ClearBladeCore import System, Query
from clearblade.ClearBladeCore import cbLogs

from cbModbus import mqtt
from cbModbus.constants import ModbusFunctionCodes

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ConnectionException, ModbusException, \
    ModbusIOException, ParameterException, NoSuchSlaveException, InvalidMessageRecievedException

ADAPTER_NAME = "modbus-client"
CB_CONFIG = {}

SCOPE_VARS = {
    'MQTT_CONNECTED': False,
    'EXIT_APP': False
}

def parse_args(argv):
    """Parse the command line arguments"""

    parser = argparse.ArgumentParser(description='Start ClearBlade Adapter')
    parser.add_argument('--systemKey', required=True, help='The System Key of the ClearBlade \
                        Plaform "System" the adapter will connect to.')

    parser.add_argument('--systemSecret', required=True, help='The System Secret of the \
                        ClearBlade Plaform "System" the adapter will connect to.')

    parser.add_argument('--deviceID', required=True, \
                        help='The id/name of the device that will be used for device \
                        authentication against the ClearBlade Platform or Edge, defined \
                        within the devices table of the ClearBlade platform.')

    parser.add_argument('--activeKey', required=True, \
                        help='The active key of the device that will be used for device \
                        authentication against the ClearBlade Platform or Edge, defined within \
                        the devices table of the ClearBlade platform.')

    parser.add_argument('--httpUrl', dest="httpURL", default="http://localhost", \
                        help='The HTTP URL of the ClearBlade Platform or Edge the adapter will \
                        connect to. The default is https://localhost.')

    parser.add_argument('--httpPort', dest="httpPort", default="9000", \
                        help='The HTTP Port of the ClearBlade Platform or Edge the adapter will \
                        connect to. The default is 9000.')

    parser.add_argument('--messagingUrl', dest="messagingURL", default="localhost", \
                        help='The MQTT URL of the ClearBlade Platform or Edge the adapter will \
                        connect to. The default is https://localhost.')

    parser.add_argument('--messagingPort', dest="messagingPort", default="1883", \
                        help='The MQTT Port of the ClearBlade Platform or Edge the adapter will \
                        connect to. The default is 9000.')

    parser.add_argument('--adapterSettingsCollection', dest="adapterSettingsCollectionName", \
                        default="", \
                        help='The name of the ClearBlade Platform data collection which contains \
                        runtime configuration settings for the adapter. The default is "".')

    parser.add_argument('--adapterSettingsItem', dest="adapterSettingsItemID", default="", \
                        help='The "item_id" of the row, within the ClearBlade Platform data \
                        collection which contains runtime configuration settings, that should \
                        be used to configure the adapter. The default is "".')

    parser.add_argument('--topicRoot', dest="adapterTopicRoot", default="", \
                        help='The root of MQTT topics this adapter will subscribe and publish to. \
                        The default is "".')

    parser.add_argument('--deviceProvisionSvc', dest="deviceProvisionSvc", default="", \
                        help='The name of a service that can be invoked to provision IoT devices \
                        within the ClearBlade Platform or Edge. The default is "".')

    parser.add_argument('--deviceHealthSvc', dest="deviceHealthSvc", default="", \
                        help='The name of a service that can be invoked to provide the health of \
                        an IoT device to the ClearBlade Platform or Edge. The default is "".')

    parser.add_argument('--deviceLogsSvc', dest="deviceLogsSvc", default="", \
                        help='The name of a service that can be invoked to provide IoT device \
                        logging information to the ClearBlade Platform or Edge. The default is "".')

    parser.add_argument('--deviceStatusSvc', dest="deviceStatusSvc", default="", \
                        help='The name of a service that can be invoked to provide the status of \
                        an IoT device to the ClearBlade Platform or Edge. The default is "".')

    parser.add_argument('--deviceDecommissionSvc', dest="deviceDecommissionSvc", default="", \
                        help='The name of a service that can be invoked to decommission IoT \
                        devices within the ClearBlade Platform or Edge. The default is "".')

    parser.add_argument('--logLevel', dest="logLevel", default="INFO", choices=['CRITICAL', \
                        'ERROR', 'WARNING', 'INFO', 'DEBUG'], help='The level of logging that \
                        should be utilized by the adapter. The default is "INFO".')

    parser.add_argument('--logCB', dest="logCB", default=False, action='store_true',\
                        help='Flag presence indicates logging information should be printed for \
                        ClearBlade libraries.')

    parser.add_argument('--logMQTT', dest="logMQTT", default=False, action='store_true',\
                        help='Flag presence indicates MQTT logs should be printed.')

    return vars(parser.parse_args(args=argv[1:]))


def setup_custom_logger(name):
    """Create a custom logger"""

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', \
                                  datefmt='%m-%d-%Y %H:%M:%S %p')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", CB_CONFIG['logLevel']))
    logger.addHandler(handler)

    return logger


def get_adapter_config():
    """Retrieve the runtime configuration for the adapter from a ClearBlade Platform data \
    collection"""
    logging.debug("Begin get_adapter_config")

    logging.debug('Retrieving the adapter configuration from data collection %s', \
        CB_CONFIG['adapterSettingsCollectionName'])

    collection = CB_SYSTEM.Collection(CB_AUTH,
                                      collectionName=CB_CONFIG['adapterSettingsCollectionName'])

    the_query = Query()
    if CB_CONFIG['adapterSettingsItemID'] != "":
        the_query.equalTo("item_id", CB_CONFIG['adapterSettingsItemID'])

    rows = collection.getItems(the_query)

    # Iterate through rows and display them
    for row in rows:
        #TODO - Implement implementation specific logic
        logging.debug(row)

    logging.debug("End get_adapter_config")


#########################
#BEGIN MQTT CALLBACKS
#########################
def on_connect(mqtt_client, userdata, flags, result_code):
    """MQTT callback invoked when a connection is established with a broker"""
    logging.debug("Begin on_connect")
    if result_code == 0:
        logging.info("Connected to ClearBlade Platform MQTT broker")
        SCOPE_VARS['MQTT_CONNECTED'] = True

        logging.info("Subscribing to MQTT topics")

        the_topic = mqtt.create_topic(CB_CONFIG['adapterTopicRoot'],\
            mqtt.MODBUS_CLIENT_TOPICS['MODBUS_REQUEST'])

        logging.debug("Subscribing to topic %s", the_topic)

        mqtt_client.subscribe(the_topic)
        mqtt_client.message_callback_add(the_topic, handle_modbus_request)

    else:
        logging.error("Error while connecting to ClearBlade Platform message broker: \
            result code = %s", result_code)

        #rc 3 = Server unavailable. If rc = 3, we don't need to do anything.
        #MQTT will keep trying to connect for us
        if result_code != 3:
            logging.fatal("Unable to connect to mqtt. ResultCode = %s", result_code)
            SCOPE_VARS['EXIT_APP'] = True

    logging.debug("End on_connect")

def on_disconnect(mqtt_client, userdata, result_code):
    """MQTT callback invoked when a connection to a broker is lost"""
    logging.debug("Begin on_disconnect")
    SCOPE_VARS['MQTT_CONNECTED'] = False

    if result_code != 0:
        logging.warning("Connection to CB Platform MQTT broker was lost, result code = %s", \
                        result_code)

        #rc 3 = Server unavailable. If rc = 3, we don't need to do anything.
        #MQTT will keep trying to connect for us
        if result_code != 3:
            SCOPE_VARS['EXIT_APP'] = True

    logging.debug("End on_disconnect")



#########################
#END MQTT CALLBACKS
#########################

def handle_modbus_request(mqtt_client, userdata, message):
    """Process the modbus request"""
    logging.debug("In handle_modbus_request")
    logging.debug("Payload = %s", message.payload)
    #{
    #   'ModbusHost': modbus.com:5023
    #   'FunctionCode': 5,
    #   'UnitID': 2,
    #   'StartAddress': 2,
    #   'AddressCount': 2,
    #   'Data': [2, 3, 4]
    # }

    logging.debug("message payload = %s", message.payload)
    payload = json.loads(message.payload.replace("'", '"'))

    if validate_modbus_request(mqtt_client, payload):
        modbus_port = payload.get('ModbusPort')
        if modbus_port is None or modbus_port == "":
            logging.info("Modbus port not specified. Defaulting port to %s", Defaults.Port)
            modbus_port = Defaults.Port

        if payload['FunctionCode'] == ModbusFunctionCodes.ReadCoil or \
            payload['FunctionCode'] == ModbusFunctionCodes.ReadDiscreteInput or \
            payload['FunctionCode'] == ModbusFunctionCodes.ReadHoldingRegisters or \
            payload['FunctionCode'] == ModbusFunctionCodes.ReadInputRegisters or \
            payload['FunctionCode'] == ModbusFunctionCodes.WriteSingleCoil or \
            payload['FunctionCode'] == ModbusFunctionCodes.WriteSingleHoldingRegister or \
            payload['FunctionCode'] == ModbusFunctionCodes.WriteMultipleCoils or \
            payload['FunctionCode'] == ModbusFunctionCodes.WriteMultipleHoldingRegisters:

            #Create a Modbus client and send the modbus request
            client = ModbusClient(payload['ModbusHost'], modbus_port)
            client.connect()

            #Send the modbus request
            response = send_modbus_request(client, payload)

            logging.debug("response = %s", response)

            # close the client
            client.close()

            if response is not None and response.get('error') is None:
                # Publish the modbus response
                logging.debug("respData = %s", response)
                mqtt.publish_modbus_response(mqtt_client, CB_CONFIG['adapterTopicRoot'], \
                    create_modbus_response(payload, response))
            else:
                mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], \
                    create_modbus_error(payload, response.get('error')))
        else:
            mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], \
                create_modbus_error(payload, \
                    "Invalid Modbus function code specified. Unable to process Modbus command."))

    logging.debug("Exit handle_modbus_request")


def validate_modbus_request(mqtt_client, payload):
    """Validate the modbus request. Publish any errors if the request is not valid."""
    #{
    #   'ModbusHost': 'localhost',
    #   'ModbusPort': 5023,
    #   'FunctionCode': 5,
    #   'UnitID': 2,
    #   'StartAddress': 2,
    #   'AddressCount': 2,
    #   'Data': [2, 3, 4]
    # }

    logging.debug("In validate_modbus_request")

    #Validate the ModbusHost value
    modbus_host = payload.get('ModbusHost')
    if modbus_host is None or modbus_host == "":
        logging.debug("Invalid ModbusHost")
        mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], create_modbus_error(\
            payload, "Modbus host not specified. Unable to process Modbus command."))
        return False

    #Validate the FunctionCode value
    func_code = payload.get('FunctionCode')
    if func_code is None or func_code == "":
        logging.debug("Invalid Modbus FunctionCode")
        mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], create_modbus_error(\
            payload, "Modbus function code not specified. Unable to process Modbus command."))
        return False

    #Validate the UnitID value
    unit_id = payload.get('UnitID')
    if unit_id is None or unit_id == "":
        logging.debug("Invalid Modbus UnitID")
        mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], create_modbus_error(\
            payload, "Modbus Unit ID not specified. Unable to process Modbus command."))
        return False

    #Validate the StartAddress value
    start_addr = payload.get('StartAddress')
    if start_addr is None or start_addr == "":
        logging.debug("Invalid Modbus StartAddress")
        mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], create_modbus_error(\
            payload, "Modbus StartAddress not specified. Unable to process Modbus command."))
        return False

    #Check if a data parameter was specified for write operations
    if payload['FunctionCode'] == ModbusFunctionCodes.WriteSingleCoil or \
        payload['FunctionCode'] == ModbusFunctionCodes.WriteSingleHoldingRegister or \
        payload['FunctionCode'] == ModbusFunctionCodes.WriteMultipleCoils or \
        payload['FunctionCode'] == ModbusFunctionCodes.WriteMultipleHoldingRegisters:

        data = payload.get('Data')
        if data is None or data == "" or len(data) == 0:
            logging.debug("Invalid Modbus Data")
            mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], \
                create_modbus_error(\
                payload, "Modbus Data not specified. Unable to process Modbus command."))
            return False
        else:
            # Validate the address count length for the write operations
            # The count length must be specified if the data array length is greater than 1
            addr_count = payload.get('AddressCount')
            if (len(data) > 0 and addr_count != len(data)) or addr_count is None or \
            addr_count == "":
                logging.debug("Invalid Modbus AddressCount")
                mqtt.publish_modbus_error(mqtt_client, CB_CONFIG['adapterTopicRoot'], \
                    create_modbus_error(\
                    payload, "Modbus address count not specified or invalid. \
                        Unable to process Modbus command."))
                return False

    logging.debug("Exit validate_modbus_request, returning True")
    return True

def send_modbus_request(client, payload):
    """Send the request to the modbus server"""
    logging.debug("In send_modbus_request")

    count = 1
    if payload.get('AddressCount') is None:
        logging.info("Modbus AddressCount not provided. Defaulting AddressCount to 1.")
    else:
        count = payload['AddressCount']


    logging.debug("payload = %s", payload)
    try:
        #Send the modbus request
        if payload['FunctionCode'] == ModbusFunctionCodes.ReadCoil:
            #Function code 1 - Read Coil
            resp = client.read_coils(payload['StartAddress'], count, \
                unit=payload['UnitID']).bits[0:count]
        elif payload['FunctionCode'] == ModbusFunctionCodes.ReadDiscreteInput:
            #Function code 2 - Read Discrete Input
            resp = client.read_discrete_inputs(payload['StartAddress'], count, \
                unit=payload['UnitID']).bits[0:count]
        elif payload['FunctionCode'] == ModbusFunctionCodes.ReadHoldingRegisters:
            #Function code 3 - Read Holding Registers
            resp = client.read_holding_registers(payload['StartAddress'], count, \
                unit=payload['UnitID']).registers[0:count]
        elif payload['FunctionCode'] == ModbusFunctionCodes.ReadInputRegisters:
            #Function code 4 - Read Input Registers
            resp = client.read_input_registers(payload['StartAddress'], count, \
                unit=payload['UnitID']).registers[0:count]
        elif payload['FunctionCode'] == ModbusFunctionCodes.WriteSingleCoil:
            #Function code 5 - Write Single Coil
            resp = client.write_coil(payload['StartAddress'], payload['Data'][0], \
                unit=payload['UnitID']).value
        elif payload['FunctionCode'] == ModbusFunctionCodes.WriteSingleHoldingRegister:
            #Function code 6 - Write Single Holding Register
            resp = client.write_register(payload['StartAddress'], payload['Data'][0], \
                unit=payload['UnitID']).value
        elif payload['FunctionCode'] == ModbusFunctionCodes.WriteMultipleCoils:
            #Function code 15 - Write Multiple Coils
            resp = client.write_coils(payload['StartAddress'], payload['Data'], \
                unit=payload['UnitID']).count
        elif payload['FunctionCode'] == ModbusFunctionCodes.WriteMultipleHoldingRegisters:
            #Function code 16 - Write Multiple Holding Registers
            resp = client.write_registers(payload['StartAddress'], payload['Data'], \
                unit=payload['UnitID']).count

        logging.debug("resp = %s", resp)

        payload = {}
        payload['Data'] = resp

        logging.debug("payload = %s", payload)
        return payload
    except ConnectionException as mce:
        logging.error("Modbus Connection Exception:: %s", str(mce))
        return { 'error': "Modbus Connection Exception: " + str(mce)}
    except ModbusIOException as mce:
        logging.error("Modbus IO Exception:: %s", str(mce))
        return { 'error': "Modbus IO Exception: " + str(mce)}
    except ParameterException as mce:
        logging.error("Modbus Parameter Exception:: %s", str(mce))
        return { 'error': "Modbus Parameter Exception: " + str(mce)}
    except NoSuchSlaveException as mce:
        logging.error("Modbus No Such Slave Exception:: %s", str(mce))
        return { 'error': "Modbus No Such Slave Exception: " + str(mce)}
    except InvalidMessageRecievedException as mce:
        logging.error("Modbus Invalid Message Received Exception:: %s", str(mce))
        return { 'error': "Modbus Invalid Message Received Exception: " + str(mce)}
    except ModbusException as mce:
        logging.error("Modbus Exception:: %s", str(mce))
        return { 'error': "Modbus Exception: " + str(mce)}

def create_modbus_response(request, resp):
    """Create a modbus response"""
    logging.debug("In create_modbus_response")
    message = {}
    message['request'] = json.dumps(request)
    message['response'] = json.dumps(resp)

    return message

def create_modbus_error(request, error):
    """Create a modbus error response"""
    logging.debug("In create_modbus_error")
    message = {}
    message['request'] = json.dumps(request)
    message['error'] = json.dumps(error)

    return message

#Main Loop
if __name__ == '__main__':

    CB_CONFIG = parse_args(sys.argv)
    LOGGER = setup_custom_logger(ADAPTER_NAME)

    if not CB_CONFIG['logCB']:
        logging.debug("Setting cbLogs.DEBUG to False")
        cbLogs.DEBUG = False

    if not CB_CONFIG['logMQTT']:
        logging.debug("Setting cbLogs.MQTT_DEBUG to False")
        cbLogs.MQTT_DEBUG = False

    logging.info("Intializing ClearBlade device client")
    logging.debug("System Key = %s", CB_CONFIG['systemKey'])
    logging.debug("System Secret = %s", CB_CONFIG['systemSecret'])
    logging.debug("HTTP URL = %s", CB_CONFIG['httpURL'] + ":" + CB_CONFIG['httpPort'])

    CB_SYSTEM = System(CB_CONFIG['systemKey'], CB_CONFIG['systemSecret'], CB_CONFIG['httpURL'] + \
                       ":" + CB_CONFIG['httpPort'])

    logging.info("Authenticating to ClearBlade")
    logging.debug("Device ID = %s", CB_CONFIG['deviceID'])
    logging.debug("Device Active Key = %s", CB_CONFIG['activeKey'])

    CB_AUTH = CB_SYSTEM.Device(CB_CONFIG['deviceID'], CB_CONFIG['activeKey'])

    #Retrieve the adapter configuration
    if CB_CONFIG['adapterSettingsCollectionName'] != "":
        logging.info("Retrieving the adapter configuration settings")
        get_adapter_config()

    #########################
    #BEGIN MQTT SPECIFIC CODE
    #########################

    #Connect to the message broker
    logging.info("Initializing the ClearBlade message broker")
    CB_MQTT = CB_SYSTEM.Messaging(CB_AUTH)

    CB_MQTT.on_connect = on_connect
    CB_MQTT.on_disconnect = on_disconnect

    logging.info("Connecting to the ClearBlade message broker")
    CB_MQTT.connect()

    #END MQTT SPECIFIC CODE

    while not SCOPE_VARS['EXIT_APP']:
        try:
            pass
        except KeyboardInterrupt:
            SCOPE_VARS['EXIT_APP'] = True
            CB_MQTT.disconnect()
            sys.exit(0)
        except Exception as e:
            logging.info("EXCEPTION:: %s", str(e))
