# Go Modbus Client Adapter

## Modbus Client Adapter
The modbus client adapter functions as a modbus master. The adapter allows an IoT gateway (or any other client) to function as a _Modbus client_ in order to access data stored on modbus devices.

Communication with the Modbus Client Adapter is enabled through MQTT. Any gateway or device wishing to retrieve data from a Modbus device should publish a JSON message the the ClearBlade Platform message broker.

## ClearBlade Platform Dependencies
The modbus client adapter adapter was constructed to provide the ability to communicate with a _System_ defined in a ClearBlade Platform instance. Therefore, the adapter requires a _System_ to have been created within a ClearBlade Platform instance.

Once a System has been created, artifacts must be defined within the ClearBlade Platform system to allow the adapter to function properly. At a minimum: 

  * An adapter configuration data collection needs to be created in the ClearBlade Platform _system_ and populated with data appropriate to the modbus client adapter adapter. The schema of the data collection should be as follows:

| Column Name      | Column Datatype |
| ---------------- | --------------- |
| adapter_name     | string          | --> _adapter_name_ MUST equal _modbusClientAdapter_
| topic_root       | string          |


## MQTT Topic Structure
The Modbus client adapter utilizes MQTT messaging to communicate with the ClearBlade Platform. The Modbus client adapter will subscribe to a specific topic in order to handle Modbus device requests. Additionally, the Modbus client adapter will publish messages to MQTT topics in order to communicate the results of requests to Modbus devices. The topic structures utilized by the Modbus client adapter are as follows:

  * Modbus Device Request: {__TOPIC ROOT__}/request
  * Modbus Device Response: {__TOPIC ROOT__}/response
  * Modbus Device Error: {__TOPIC ROOT__}/error

## MQTT Message structure

### Modbus Device Request Payload Format
The payload of a Modbus Device Request should have the following

```js
/**
 * @typedef Request
 * @parameter {string} ModbusHost IP Address of ModbusHost
 * @parameter {number} FunctionCode Modbus function to execute on the Modbus device
 * @parameter {number} StartAddress address associated with the coil/register to be accessed
 * @parameter {number} AddressCount number of sequential addresses to be accessed
 * @parameter {number[]} Data - Array of integers (register requests) or booleans (coil/contact requests)
 * @example
      {
            "ModbusHost": "192.168.0.9:502",
            "FunctionCode": 1, 
            "StartAddress": 0, 
            "AddressCount": 3, 
            "Data": [2, 3, 4] 
      }
 */
```

[//]: TODO_Add_Identifier_to_JSON

   __*Where*__ 

   __ModbusHost__
  * REQUIRED
  * The host name and port of the modbus server to contact

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

### Modbus Device Response Payload Format

```js

/**
 * @typedef Response
 * @parameter {Request} request
 * @parameter {Object} response
 * @param {number|number[]} response.Data number (or array) depending on Function code
 * @example

    {
      "request": {
            "ModbusHost": "192.168.0.9:502",
            "FunctionCode": 1, 
            "StartAddress": 0, 
            "AddressCount": 3, 
            "Data": [2, 3, 4] 
      },
      "response": {
          "Data": [45,2,5]
      }
    }
  */
```

   __*Where*__ 

   __response.Data__
  * Will contain an array of boolean values, for function codes 1 and 2
  * Will contain an array of 16-bit integers, for function codes 3 and 4
  * Will contain an array with a single boolean value representing the value written to the coil, for function code 5
  * Will contain an array with a single 16-bit value representing the value written to the register, for function code 6
  * Will contain an array with a single integer value representing the number of coils written to, for function code 15
  * Will contain an array with a single integer value representing the number of registers written to, for function code 16

### Modbus Device Error Response Payload Format

```js

/**
 * @typedef Response
 * @parameter {Request} request
 * @parameter {string} error
 * @example

      {
      "request": {
            "ModbusHost": "192.168.0.9:502",
            "FunctionCode": 1, 
            "StartAddress": 0, 
            "AddressCount": 3, 
            "Data": [2, 3, 4] 
      },
      "error": "malformed JSON"
    }
  */
```

   __*Where*__ 

   __error__
  * Will contain a string describing the error condition encountered

## Executing the adapter
`modbusClientAdapter -systemKey=<PLATFORM SYSTEM KEY> -systemSecret=<PLATFORM SYSTEM KEY> -deviceID=<AUTH DEVICE NAME> -activeKey=<AUTH DEVICE ACTIVE KEY> -platformURL=<CB PLATFORM URL> -messagingURL=<CB PLATFORM MESSAGING URL> -adapterConfigCollectionID=<CB DATA COLLECTION NAME> -topicRoot=<MQTT_TOPIC_ROOT> -logLevel=<LOG LEVEL>`

   __*Where*__ 

   __systemKey__
  * REQUIRED
  * The system key of the ClearBLade Platform __System__ the adapter will connect to

   __systemSecret__
  * REQUIRED
  * The system secret of the ClearBLade Platform __System__ the adapter will connect to
   
   __deviceID__
  * REQUIRED
  * The device name the modbus client adapter will use to authenticate to the ClearBlade Platform
  * Requires the device to have been defined in the _Auth - Devices_ collection within the ClearBlade Platform __System__
   
   __activeKey__
  * REQUIRED
  * The active key the adapter will use to authenticate to the platform
  * Requires the device to have been defined in the _Auth - Devices_ collection within the ClearBlade Platform __System__
   
   __platformURL__
  * The url (including the port number) of the ClearBlade Platform instance the adapter will connect to
  * OPTIONAL
  * Defaults to __http://localhost:9000__

   __messagingUrl__
  * The MQTT url (including the port number) of the ClearBlade Platform instance the adapter will connect to
  * OPTIONAL
  * Defaults to __localhost:1883__

   __adapterConfigCollectionID__
  * See the _Runtime Configuration_ section below
  * OPTIONAL

   __topicRoot__
  * The root hierarchy of the MQTT topic tree that should be used when subscribing to MQTT topics or publishing to MQTT topics
  * OPTIONAL

   __logLevel__
  * The level of runtime logging the adapter should provide.
  * Available log levels:
    * fatal
    * error
    * warn
    * info
    * debug
  * OPTIONAL
  * Defaults to __info__
  * Logging information will automatically be written to __/var/log/modbusClientAdapter__

## Runtime Configuration

### Modbus Client Adapter
Runtime configuration, utilizing the data collection described in the _ClearBlade Platform Dependencies_ section above, provides the ability to specify an MQTT topic root dynamically. If a topic root is specified in the data collection, the topic root specified in the data collection will override any topic root specified on the command line when starting the adapter. When the topic root is specified, or modified, within the data collection, the modbus client adapter __MUST__ be restarted in order for the changes to be in effect at runtime.

## Setup
---
The mtsIo adapter is dependent upon the ClearBlade Go SDK and its dependent libraries being installed. The mtsIo adapter was written in Go and therefore requires Go to be installed (https://golang.org/doc/install).

### Adapter compilation
In order to compile the adapter for execution, the following steps need to be performed:

 1. Retrieve the adapter source code  
    * ```git clone git@github.com:ClearBlade/Modbus-Adapter.git```
 2. Navigate to the _modbusClientAdapter_ directory  
    * ```cd go/modbusClientAdapter```
 3. Compile the adapter
    * ```GOARCH=arm GOARM=5 GOOS=linux go build```


