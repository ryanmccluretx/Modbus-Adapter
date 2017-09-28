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

_Construction in progress_

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

   *Where* 

   __systemKey__
  * REQUIRED
  * The system key of the ClearBLade Platform __System__ the adapter will connect to

   __systemSecret__
  * REQUIRED
  * The system secret of the ClearBLade Platform __System__ the adapter will connect to
   
   __deviceID__
  * REQUIRED
  * The device name the BLE adapter will use to authenticate to the ClearBlade Platform
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
  * The MQTT port number of the ClearBlade Platform instance the adapter will connect to
  * See the _Runtime Configuration_ section below
  * OPTIONAL

   __adapterSettingsItem__
  * The MQTT port number of the ClearBlade Platform instance the adapter will connect to
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

#### Modbus Client Adapter

_Development in progress_

### Runtime Configuration

#### Modbus Server Adapter
TBD - Runtime configuration currently not needed

#### Modbus Client Adapter

## Setup
---
The python adapters are dependent upon the ClearBlade Python SDK and its dependent libraries being installed. In addition, a third-party library (https://github.com/riptideio/pymodbus) providing Modbus functionality is being utilized. To install the dependent libraries:

execute 

`git clone git@github.com:ClearBlade/Modbus-Adapter.git` 
`cd python` 
`python setup.py install`

__OR__

`pip install  -U pymodbus` 
`pip install -U clearblade`

## Todo
---
 - Complete construction of Modbus client adapter

