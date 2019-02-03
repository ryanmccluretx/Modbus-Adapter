# Python Modbus Adapter

The Python __Modbus__ adapters provide the ability for devices that __do not__ natively commicate using the Modbus protocol to interact with devices that __do__ communicate using the Modbus protocol.

The Python Modbus adapter is composed of two separate adapters:
  1. Modbus client (Modbus master) adapter
  2. Mobus server (Modbus slave) adapter

Whether or not both adapters are utilized will be implementation specific.

### Modbus Server Adapter
The modbus server adapter functions as a modbus server proxy. The adapter allows _Modbus clients_ to access non-modbus devices. The adapter assumes that non-modbus device data will be stored in data collections within a ClearBlade Platform _system_. The data collections utilized by the adapter align to the 4 data tables defined in the modbus spec:

  1. Discrete Input Contacts - Boolean values, read-only
  2. Discrete Output Coils - Boolean values, read/write
  3. Analog Input Registers - 16bit integer values, read-only
  4. Analog Output Holding Registers - 16bit integer values, read/write

Each of the data collections contains columns representing the Modbus Unit ID (slave ID), modbus data address, and modbus data value. Non-modbus devices will need their data stored in the 4 collections in order for the adapter to access the data appropriately. 

### Modbus Client Adapter
The modbus client adapter functions as a modbus master. The adapter allows an IoT gateway (or any other client) to function as a _Modbus client_ in order to access data stored on modbus devices.

Communication with the Modbus Client Adapter is enabled through MQTT. Any gateway or device wishing to retrieve data from a Modbus device should publish a JSON message the the ClearBlade Platform message broker.

#### MQTT Topic Structure
The Modbus client adapter utilizes MQTT messaging to communicate with the ClearBlade Platform. The Modbus client adapter will subscribe to a specific topic in order to handle Modbus device requests. Additionally, the Modbus client adapter will publish messages to MQTT topics in order to communicate the results of requests to Modbus devices. The topic structures utilized by the Modbus client adapter are as follows:

  * Modbus Device Request: {__TOPIC ROOT__}/modbus/command/request
  * Modbus Device Response: {__TOPIC ROOT__}/modbus/command/response
  * Modbus Device Error: {__TOPIC ROOT__}/modbus/command/error

#### MQTT Message structure

##### Modbus Device Request Payload Format
The payload of a Modbus Device Request should have the following

```json
    {
      'ModbusHost': 'modbushost' --> String
      'FunctionCode': modbus_port, --> Integer
      'UnitID': device_unit_id, --> Integer
      'StartAddress': start_address, --> Integer
      'AddressCount': address_count, --> Integer
      'Data': [2, 3, 4] --> Array of integers (register requests) or booleans (coil/contact requests)
    }
```

   __*Where*__ 

   __ModbusHost__
  * REQUIRED
  * The host name of the modbus server to contact

   __FunctionCode__
  * REQUIRED
  * The Modbus function to execute on the Modbus device
    * 1 - Read Coil
    * 2 - Read Discrete Input
    * 3 - Read Holding Registers
    * 4 - Read Input Registers
    * 5 - Write Single Coil
    * 6 - Write Single Holding Register
    * 15 - Write Multiple Coils
    * 16 - Write Multiple Holding Registers

   __UnitID__
  * REQUIRED
  * The Modbus Unit ID associated with the Modbus device to access

   __StartAddress__
  * REQUIRED
  * The address associated with the coil/register to be accessed

   __AddressCount__
  * OPTIONAL
  * If more than one coil/register are to be accessed, the AddressCount property indicates the number of sequential addresses to be accessed, beginning with the address specified by the StartAddress property.
   
   __Data__
  * REQUIRED for function codes 5, 6, 15, and 16
  * The data to be written to Modbus device coils/registers, contained within an array
  * Modbus coils store boolean only data. Function codes 5 and 15, therefore, require an array of boolean values.
    * [true, false, true, true, etc.]
  * Modbus registers store 16 bit registers. Function codes 6 and 16, therefore, require an array of integer values.
    * [5, 246, 34, etc.]

##### Modbus Device Response Payload Format

```json
    {
      'request': {
          'ModbusHost': 'modbushost' --> String
          'FunctionCode': modbus_port, --> Integer
          'UnitID': device_unit_id, --> Integer
          'StartAddress': start_address, --> Integer
          'AddressCount': address_count, --> Integer
          'Data': [2, 3, 4] --> Array of integers (register requests) or booleans (coil requests)
      },
      'response': {
          'Data': response_data --> will be an individual value or an array, depending on the function code
      }
    }
```

   __*Where*__ 

   __response.Data__
  * Will contain an array of boolean values, for function codes 1 and 2
  * Will contain an array of 16-bit integers, for function codes 3 and 4
  * Will contain a single boolean value representing the value written to the coil, for function code 5
  * Will contain a single 16-bit value representing the value written to the register, for function code 6
  * Will contain a single integer value representing the number of coils written to, for function code 15
  * Will contain a single integer value representing the number of registers written to, for function code 16

##### Modbus Device Error Response Payload Format

```json
    {
      'request': {
          'ModbusHost': 'modbushost' --> String
          'FunctionCode': modbus_port, --> Integer
          'UnitID': device_unit_id, --> Integer
          'StartAddress': start_address, --> Integer
          'AddressCount': address_count, --> Integer
          'Data': [2, 3, 4] --> Array of integers (register requests) or booleans (coil/contact requests)
      },
      'error': error_message
    }
```

   __*Where*__ 

   __error__
  * Will contain a string describing the error condition encountered

## ClearBlade Platform Dependencies
The Python Modbus adapters were constructed to provide the ability to communicate with a _System_ defined in a ClearBlade Platform instance. Therefore, the adapters require a _System_ to have been created within a ClearBlade Platform instance.

Once a System has been created, artifacts must be defined within the ClearBlade Platform system to allow the adapters to function properly. At a minimum: 

  * A device needs to be created in the Auth --> Devices collection. The device will represent the adapter, or more importantly the IoT gateway, on which the adapter is executing. The _name_ and _active key_ values specified in the Auth --> Devices collection will be used by the adapter to authenticate to the ClearBlade Platform or ClearBlade Edge. 
  * The 4 Modbus specific data collections need to be created in the ClearBlade Platform _system_ and populated with the data appropriate to the devices that will be accessed. The schema for each of the data collections should be as follows:

### Discrete Input Contacts Schema

| Column Name   | Column Datatype |
| ------------- | --------------- |
| unit_id       | int             |
| data_address  | int             |
| data_value    | bool            |

### Discrete Output Coils Schema

| Column Name   | Column Datatype |
| ------------- | --------------- |
| unit_id       | int             |
| data_address  | int             |
| data_value    | bool            |

### Analog Input Registers Schema

| Column Name   | Column Datatype |
| ------------- | --------------- |
| unit_id       | int             |
| data_address  | int             |
| data_value    | int             |

### Analog Output Holding Registers Schema

| Column Name   | Column Datatype |
| ------------- | --------------- |
| unit_id       | int             |
| data_address  | int             |
| data_value    | int             |

## Usage
The modbus adapters were written to be compatible with both Python 2 and Python 3. 

### Executing the adapters

#### Modbus Server Adapter

##### Python 2
`python modbus-server-adapter.py --systemKey=<PLATFORM SYSTEM KEY> --systemSecret=<PLATFORM SYSTEM SECRET> --deviceID=<AUTH DEVICE NAME> --activeKey=<AUTH DEVICE ACTIVE KEY> --httpUrl=<CB PLATFORM URL> --httpPort=<CB PLATFORM PORT> --messagingUrl=<CB PLATFORM MESSAGING URL> --messagingPort=<CB PLATFORM MESSAGING PORT> --adapterSettingsCollection=<CB DATA COLLECTION NAME> --adapterSettingsItem=<ROW ITEM ID VALUE> --topicRoot=<TOPIC ROOT> --deviceProvisionSvc=<PROVISIONING SERVICE NAME> --deviceHealthSvc=<HEALTH SERVICE NAME> --deviceLogsSvc=<DEVICE LOGS SERVICE NAME> --deviceStatusSvc=<DEVICE STATUS SERVICE NAME> --deviceDecommissionSvc=<DECOMMISSION SERVICE NAME> --logLevel=<LOG LEVEL> --logCB --logMQTT --modbusZeroMode --modbusPort=<MODBUS TCP SERVER PORT> --inputContactsCollection=<DISCRETE INPUT CONTACTS COLLECTION NAME> --outputCoilsCollection=<DISCRETE OUTPUT COILS COLLECTION NAME> --inputRegisterCollection=<ANALOG INPUT REGISTERS COLLECTION NAME> --outputRegisterCollection<ANALOG OUTPUT HOLDING REGISTERS COLLECTION NAME>`

##### Python 3
`python3 modbus-server-adapter.py --systemKey=<PLATFORM SYSTEM KEY> --systemSecret=<PLATFORM SYSTEM SECRET> --deviceID=<AUTH DEVICE NAME> --activeKey=<AUTH DEVICE ACTIVE KEY> --httpUrl <CB PLATFORM URL> --httpPort=<CB PLATFORM PORT> --messagingUrl=<CB PLATFORM MESSAGING URL> --messagingPort=<CB PLATFORM MESSAGING PORT> --adapterSettingsCollection=<CB DATA COLLECTION NAME> --adapterSettingsItem=<ROW ITEM ID VALUE> --topicRoot=<TOPIC ROOT> --deviceProvisionSvc=<PROVISIONING SERVICE NAME> --deviceHealthSvc=<HEALTH SERVICE NAME> --deviceLogsSvc=<DEVICE LOGS SERVICE NAME> --deviceStatusSvc=<DEVICE STATUS SERVICE NAME> --deviceDecommissionSvc=<DECOMMISSION SERVICE NAME> --logLevel=<LOG LEVEL> --logCB --logMQTT --modbusZeroMode --modbusPort=<MODBUS TCP SERVER PORT> --inputContactsCollection=<DISCRETE INPUT CONTACTS COLLECTION NAME> --outputCoilsCollection=<DISCRETE OUTPUT COILS COLLECTION NAME> --inputRegisterCollection=<ANALOG INPUT REGISTERS COLLECTION NAME> --outputRegisterCollection<ANALOG OUTPUT HOLDING REGISTERS COLLECTION NAME>`

#### Modbus Client Adapter

##### Python 2
`python modbus-client-adapter.py --systemKey=<PLATFORM SYSTEM KEY> --systemSecret=<PLATFORM SYSTEM SECRET> --deviceID=<AUTH DEVICE NAME> --activeKey=<AUTH DEVICE ACTIVE KEY> --httpUrl=<CB PLATFORM URL> --httpPort=<CB PLATFORM PORT> --messagingUrl=<CB PLATFORM MESSAGING URL> --messagingPort=<CB PLATFORM MESSAGING PORT> --adapterSettingsCollection=<CB DATA COLLECTION NAME> --adapterSettingsItem=<ROW ITEM ID VALUE> --topicRoot=<TOPIC ROOT> --deviceProvisionSvc=<PROVISIONING SERVICE NAME> --deviceHealthSvc=<HEALTH SERVICE NAME> --deviceLogsSvc=<DEVICE LOGS SERVICE NAME> --deviceStatusSvc=<DEVICE STATUS SERVICE NAME> --deviceDecommissionSvc=<DECOMMISSION SERVICE NAME> --logLevel=<LOG LEVEL> --logCB --logMQTT`

##### Python 3
`python3 modbus-client-adapter.py --systemKey=<PLATFORM SYSTEM KEY> --systemSecret=<PLATFORM SYSTEM SECRET> --deviceID=<AUTH DEVICE NAME> --activeKey=<AUTH DEVICE ACTIVE KEY> --httpUrl <CB PLATFORM URL> --httpPort=<CB PLATFORM PORT> --messagingUrl=<CB PLATFORM MESSAGING URL> --messagingPort=<CB PLATFORM MESSAGING PORT> --adapterSettingsCollection=<CB DATA COLLECTION NAME> --adapterSettingsItem=<ROW ITEM ID VALUE> --topicRoot=<TOPIC ROOT> --deviceProvisionSvc=<PROVISIONING SERVICE NAME> --deviceHealthSvc=<HEALTH SERVICE NAME> --deviceLogsSvc=<DEVICE LOGS SERVICE NAME> --deviceStatusSvc=<DEVICE STATUS SERVICE NAME> --deviceDecommissionSvc=<DECOMMISSION SERVICE NAME> --logLevel=<LOG LEVEL> --logCB --logMQTT`


   __*Where*__ 

   __systemKey__
  * REQUIRED
  * The system key of the ClearBLade Platform __System__ the adapter will connect to

   __systemSecret__
  * REQUIRED
  * The system secret of the ClearBLade Platform __System__ the adapter will connect to
   
   __deviceID__
  * REQUIRED
  * The device name the modbus adapter will use to authenticate to the ClearBlade Platform
  * Requires the device to have been defined in the _Auth - Devices_ collection within the ClearBlade Platform __System__
   
   __activeKey__
  * REQUIRED
  * The active key the adapter will use to authenticate to the platform
  * Requires the device to have been defined in the _Auth - Devices_ collection within the ClearBlade Platform __System__
   
   __httpUrl__
  * The url (without the port number) of the ClearBlade Platform instance the adapter will connect to
  * OPTIONAL
  * Defaults to __http://localhost__

   __httpPort__
  * The port number of the ClearBlade Platform instance the adapter will connect to
  * OPTIONAL
  * Defaults to __9000__

   __messagingUrl__
  * The MQTT url (without the port number) of the ClearBlade Platform instance the adapter will connect to
  * OPTIONAL
  * Defaults to __localhost__

   __messagingPort__
  * The MQTT port number of the ClearBlade Platform instance the adapter will connect to
  * OPTIONAL
  * Defaults to __1883__

   __adapterSettingsCollection__
  * See the _Runtime Configuration_ section below
  * OPTIONAL

   __adapterSettingsItem__
  * See the _Runtime Configuration_ section below
  * OPTIONAL

   __topicRoot__
  * The root hierarchy of the MQTT topic tree that should be used when subscribing to MQTT topics or publishing to MQTT topics
  * OPTIONAL

   __deviceProvisionSvc__
  * The name of a service, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can invoke to provision IoT devices on the ClearBlade Platform or ClearBlade Edge.
  * Dependent upon MQTT. The adapter will publish data to a MQTT topic on the platform message broker containing relevant device information whenever the adapter needs to provision an IoT device on the ClearBlade Platform or ClearBlade Edge.
  * __Implementation specific. Will need to be implemented by the developer.__
  * OPTIONAL

   __deviceHealthSvc__
  * The name of a service, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can invoke to provide health information about connected IoT devices to the ClearBlade Platform or ClearBlade Edge.
  * Dependent upon MQTT. The adapter will publish data to a MQTT topic on the platform message broker containing relevant health information.
  * __Implementation specific. Will need to be implemented by the developer.__
  * OPTIONAL

   __deviceLogsSvc__
  * The name of a service, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can invoke to provide device log entries to the ClearBlade Platform or ClearBlade Edge.
  * Dependent upon MQTT. The adapter will publish data to a MQTT topic on the platform message broker containing relevant log entries.
  * __Implementation specific. Will need to be implemented by the developer.__
  * OPTIONAL

   __deviceStatusSvc__
  * The name of a service, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can invoke to provide the status of connected IoT devices to the ClearBlade Platform or ClearBlade Edge.
  * Dependent upon MQTT. The adapter will publish data to a MQTT topic on the platform message broker containing relevant device status information.
  * __Implementation specific. Will need to be implemented by the developer.__
  * OPTIONAL

   __deviceDecommissionSvc__
  * The name of a service, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can invoke to decommission IoT devices.
  * Dependent upon MQTT. The adapter will publish a MQTT topic on the platform message broker containing relevant device information whenver the adapter needs to decommission an IoT device.
  * __Implementation specific. Will need to be implemented by the developer.__
  * OPTIONAL

   __logLevel__
  * The level of runtime logging the adapter should provide.
  * A developer can utilize the standard logging library provided by the python to add implemenation specific log information:
    * logging.critical
    * logging.error
    * logging.warning
    * logging.info
    * logging.debug
  * Available options are:
    * CRITICAL
    * ERROR
    * WARNING
    * INFO
    * DEBUG
  * OPTIONAL
  * Defaults to __INFO__

   __logCB__
  * Indicates whether or not log entries from the ClearBlade Python SDK should be printed
  * OPTIONAL
  * The presence of this command line argument indicates to the adapter that you wish to display ClearBlade SDK log information

   __logMQTT__
  * Indicates whether or not MQTT log entries should be printed
  * OPTIONAL
  * The presence of this command line argument indicates to the adapter that you wish to display MQTT log information

  __modbusZeroMode__ 
  * Indicates whether Modbus Zero Mode should be used
  * A request to address(0-7) will map to the address (0-7). The default (without the modbusZeroMode arg) is based on section 4.4 of the specification, so address(0-7) will map to (1-8)
  * OPTIONAL
  * The presence of this command line argument indicates that Modbus Zero Mode should be used

   __modbusPort__
  * The port number the Modbus TCP server should listen to
  * OPTIONAL
  * Defaults to __5020__

   __inputContactsCollection__
  * The name of a data collection, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can iquery to retrieve read-only Modbus input contacts (coils).
  * OPTIONAL
  * Default value is __Discrete\_Input\_Contacts__

   __outputCoilsCollection__
  * The name of a data collection, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can iquery to retrieve Modbus input coils.
  * OPTIONAL
  * Default value is __Discrete\_Output\_Coils__

   __inputRegisterCollection__
  * The name of a data collection, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can iquery to retrieve read-only Modbus analog input registers.
  * OPTIONAL
  * Default value is __Analog\_Input\_Registers__

   __outputRegisterCollection__
  * The name of a data collection, defined within the ClearBlade Platform or ClearBlade Edge, the adapter can iquery to retrieve read-only Modbus analog holding registers.
  * OPTIONAL
  * Default value is __Analog\_Output\_Holding\_Registers__

### Runtime Configuration

#### Modbus Server Adapter
Runtime configuration currently not being utilized as it is currently not needed.

#### Modbus Client Adapter
Runtime configuration currently not being utilized as it is currently not needed.

## Setup
---
The python adapters are dependent upon the ClearBlade Python SDK and its dependent libraries being installed. In addition, a third-party library (https://github.com/riptideio/pymodbus) providing Modbus functionality is being utilized. To install the dependent libraries:

execute 
```
git clone git@github.com:ClearBlade/Modbus-Adapter.git 
cd python 
python setup.py install
```

__OR__

```
pip install  -U pymodbus 
pip install -U clearblade
```


