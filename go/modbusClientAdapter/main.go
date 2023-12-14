package main

import (
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"net"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	modbus "github.com/goburrow/modbus"

	cb "github.com/clearblade/Go-SDK"
	mqttTypes "github.com/clearblade/mqtt_parsing"
	mqtt "github.com/clearblade/paho.mqtt.golang"
	"github.com/hashicorp/logutils"
)

const (
	platURL                        = "http://localhost:9000"
	messURL                        = "localhost:1883"
	msgSubscribeQos                = 0
	msgPublishQos                  = 0
	JavascriptISOString            = "2006-01-02T15:04:05.000Z07:00"
	tcpTimeout                     = 10 * time.Second
	tcpIdleTimeout                 = 60 * time.Second
	adapterConfigCollectionDefault = "adapter_config"
)

var (
	platformURL               string //Defaults to http://localhost:9000
	messagingURL              string //Defaults to localhost:1883
	sysKey                    string
	sysSec                    string
	deviceName                string //Defaults to modbusClientAdapter
	activeKey                 string
	logLevel                  string //Defaults to info
	adapterConfigCollection   string
	topicRoot                 string
	cbBroker                  cbPlatformBroker
	cbSubscribeChannel        <-chan *mqttTypes.Publish
	endSubscribeWorkerChannel chan string
	adapterID                 string
	modbusHandler             *modbus.TCPClientHandler
	modbusClient              modbus.Client
)

type cbPlatformBroker struct {
	name         string
	clientID     string
	client       *cb.DeviceClient
	platformURL  *string
	messagingURL *string
	systemKey    *string
	systemSecret *string
	username     *string
	password     *string
	topic        string
	qos          int
}

func init() {
	flag.StringVar(&sysKey, "systemKey", "", "system key (required)")
	flag.StringVar(&sysSec, "systemSecret", "", "system secret (required)")
	flag.StringVar(&deviceName, "deviceID", "modbusClientAdapter", "name of device (optional)")
	flag.StringVar(&activeKey, "activeKey", "", "active key for device authentication (required)")
	flag.StringVar(&platformURL, "platformURL", platURL, "platform url (optional)")
	flag.StringVar(&messagingURL, "messagingURL", messURL, "messaging URL (optional)")
	flag.StringVar(&adapterConfigCollection, "adapterConfigCollection", adapterConfigCollectionDefault, "The name of the data collection used to house adapter configuration (optional)")
	flag.StringVar(&topicRoot, "topicRoot", "modbus/command", "The root of all MQTT topics that should be used to publish/subscribe to (optional)")
	flag.StringVar(&logLevel, "logLevel", "info", "The level of logging to use. Available levels are 'debug, 'info', 'warn', 'error', 'fatal' (optional)")
	flag.StringVar(&adapterID, "adapterID", "", "Unique identifier for this adapter, typically SiteID where modbus adapter is deployed (optional)")

}

func usage() {
	log.Printf("Usage: modbusClientAdapter [options]\n\n")
	flag.PrintDefaults()
}

func validateFlags() {
	flag.Parse()

	if sysKey == "" || sysSec == "" || activeKey == "" {

		log.Printf("ERROR - Missing required flags\n\n")
		flag.Usage()
		os.Exit(1)
	}
}

func main() {
	fmt.Println("Starting modbusClientAdapter...")

	rand.Seed(time.Now().UnixNano())

	//Validate the command line flags
	flag.Usage = usage
	validateFlags()

	//Initialize the logging mechanism
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	filter := &logutils.LevelFilter{
		Levels:   []logutils.LogLevel{"DEBUG", "INFO", "WARN", "ERROR", "FATAL"},
		MinLevel: logutils.LogLevel(strings.ToUpper(logLevel)),
		Writer:   os.Stdout,
	}
	log.SetOutput(filter)

	cbBroker = cbPlatformBroker{

		name:         "ClearBlade",
		clientID:     deviceName + "_client" + "-" + strconv.Itoa(rand.Intn(10000)),
		client:       nil,
		platformURL:  &platformURL,
		messagingURL: &messagingURL,
		systemKey:    &sysKey,
		systemSecret: &sysSec,
		username:     &deviceName,
		password:     &activeKey,
		qos:          msgSubscribeQos,
	}

	// Initialize ClearBlade Client
	if err := initCbClient(cbBroker); err != nil {
		log.Println(err.Error())
		log.Println("Unable to initialize CB broker client. Exiting.")
		return
	}

	defer close(endSubscribeWorkerChannel)
	endSubscribeWorkerChannel = make(chan string)

	//Handle OS interrupts to shut down gracefully
	c := make(chan os.Signal, 1)
	signal.Notify(c, syscall.SIGINT, syscall.SIGTERM)
	sig := <-c

	log.Printf("[INFO] OS signal %s received, ending go routines.", sig)

	//End the existing goRoutines
	endSubscribeWorkerChannel <- "Stop Channel"
	os.Exit(0)
}

// ClearBlade Client init helper
func initCbClient(platformBroker cbPlatformBroker) error {
	log.Println("[DEBUG] initCbClient - Initializing the ClearBlade client")

	cbBroker.client = cb.NewDeviceClientWithAddrs(*(platformBroker.platformURL), *(platformBroker.messagingURL), *(platformBroker.systemKey), *(platformBroker.systemSecret), *(platformBroker.username), *(platformBroker.password))

	for _, err := cbBroker.client.Authenticate(); err != nil; {
		log.Printf("[ERROR] initCbClient - Error authenticating %s: %s\n", platformBroker.name, err.Error())
		log.Println("[ERROR] initCbClient - Will retry in 1 minute...")

		// sleep 1 minute
		time.Sleep(time.Duration(time.Minute * 1))
		_, err = cbBroker.client.Authenticate()
	}

	//Retrieve adapter configuration data
	log.Println("[INFO] main - Retrieving adapter configuration...")
	getAdapterConfig()

	log.Println("[DEBUG] initCbClient - Initializing MQTT")
	callbacks := cb.Callbacks{OnConnectionLostCallback: OnConnectLost, OnConnectCallback: OnConnect}
	if err := cbBroker.client.InitializeMQTTWithCallback(platformBroker.clientID, "", 30, nil, nil, &callbacks); err != nil {
		log.Fatalf("[FATAL] initCbClient - Unable to initialize MQTT connection with %s: %s", platformBroker.name, err.Error())
		return err
	}

	return nil
}

//If the connection to the broker is lost, we need to reconnect and
//re-establish all of the subscriptions
func OnConnectLost(client mqtt.Client, connerr error) {
	log.Printf("[INFO] OnConnectLost - Connection to broker was lost: %s\n", connerr.Error())

	//End the existing goRoutines
	endSubscribeWorkerChannel <- "Stop Channel"

	//We can't rely on MQTT auto-reconnect because it is most likely that our auth token expired
	//When the connection is lost, just exit
	log.Fatalln("[FATAL] onConnectLost - MQTT Connection was lost. Stopping Adapter to force device reauth.")
}

//When the connection to the broker is complete, set up the subscriptions
func OnConnect(client mqtt.Client) {
	topic := topicRoot + "/request"
	log.Println("[INFO] OnConnect - Connected to ClearBlade Platform MQTT broker on topic:", topic)

	//CleanSession, by default, is set to true. This results in non-durable subscriptions.
	//We therefore need to re-subscribe
	log.Println("[DEBUG] OnConnect - Begin Configuring Subscription(s)")

	var err error
	for cbSubscribeChannel, err = subscribe(topic); err != nil; {
		//Wait 30 seconds and retry
		log.Printf("[ERROR] OnConnect - Error subscribing to MQTT: %s\n", err.Error())
		log.Println("[ERROR] OnConnect - Will retry in 30 seconds...")
		time.Sleep(time.Duration(30 * time.Second))
		cbSubscribeChannel, err = subscribe(topicRoot + "/request")
	}

	//Start subscribe worker
	go subscribeWorker()
}

func subscribeWorker() {
	log.Println("[INFO] subscribeWorker - Starting subscribeWorker")

	log.Println("[INFO] subscribeWorker - Initializing the modbus handler")
	modbusHandler = &modbus.TCPClientHandler{}
	modbusHandler.Timeout = tcpTimeout
	modbusHandler.IdleTimeout = tcpIdleTimeout
	modbusHandler.SlaveId = 255
	log.Printf("[DEBUG] subscribeWorker - Slave ID set to %d\n", modbusHandler.SlaveId)
	modbusHandler.Timeout = 5 * time.Second

	if strings.ToUpper(logLevel) == "DEBUG" {
		modbusHandler.Logger = log.New(os.Stdout, "", log.LstdFlags|log.Lshortfile)
	}

	defer modbusHandler.Close()

	//Wait for subscriptions to be received
	log.Println("[INFO] subscribeWorker - Waiting for modbus requests")
	for {
		select {
		case message, ok := <-cbSubscribeChannel:
			if ok {
				log.Println("[INFO] subscribeWorker - request received")
				handleRequest(message.Payload)
			}
		case _ = <-endSubscribeWorkerChannel:
			//End the current go routine when the stop signal is received
			log.Println("[INFO] subscribeWorker - Stopping subscribeWorker")
			return
		}
	}
}

func resetModbusClient(address string) (err error) {
	log.Printf("[DEBUG] resetModbusClient - new address = %s\n", address)
	log.Println("[DEBUG] resetModbusClient - Closing modbus handler")
	modbusHandler.Close()

	if address == "" {
		log.Printf("[DEBUG] resetModbusClient - Invalid address for modbus host: %s\n", address)
		return fmt.Errorf("Invalid address for modbus host: %s", address)
	}

	modbusHandler.Address = address

	// Connect to modbus manually so that multiple requests are handled in one connection session
	log.Println("[DEBUG] resetModbusClient - Connecting modbus handler")
	if err = modbusHandler.Connect(); err != nil {
		//We need to reset the address to blank in order to avoid a nil pointer exception in the
		//handleModbusRequest function
		modbusHandler.Address = ""
		return
	}
	modbusClient = modbus.NewClient(modbusHandler)
	return
}

func handleRequest(payload []byte) {
	// The json request should resemble the following:
	//{
	//'ModbusHost': modbus.com:5023
	//'FunctionCode': 5,
	//'StartAddress': 2,
	//'AddressCount': 2,
	//'Data': [2, 3, 4]
	//}
	log.Println("[INFO] handleRequest - processing request")
	log.Printf("[DEBUG] handleRequest - Json payload received: %s\n", string(payload))

	var jsonPayload map[string]interface{}
	var errorCode = 0

	if err := json.Unmarshal(payload, &jsonPayload); err != nil {
		log.Printf("[ERROR] handleRequest - Error encountered unmarshalling json: %s\n", err.Error())
		addErrorToPayload(jsonPayload, "Error encountered unmarshalling json: "+err.Error(), errorCode)
		jsonPayload["request"] = payload
	} else {
		log.Printf("[DEBUG] handleRequest - Json payload received: %#v\n", jsonPayload)
	}

	if jsonPayload["ModbusHost"] == nil {
		log.Println("[ERROR] handleRequest - ModbusHost not specified in incoming payload")
		addErrorToPayload(jsonPayload, "ModbusHost is required", errorCode)
		jsonPayload["request"] = payload
	}

	if jsonPayload["FunctionCode"] == nil {
		log.Println("[ERROR] handleRequest - FunctionCode not specified in incoming payload")
		addErrorToPayload(jsonPayload, "FunctionCode is required", errorCode)
		jsonPayload["request"] = payload
	} else {

		log.Printf("[DEBUG] FunctionCode received = %d", uint16(jsonPayload["FunctionCode"].(float64)))

		if uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeReadDiscreteInputs &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeReadCoils &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeWriteSingleCoil &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeWriteMultipleCoils &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeReadInputRegisters &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeReadHoldingRegisters &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeWriteSingleRegister &&
			uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeWriteMultipleRegisters {
			//uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeReadWriteMultipleRegisters {
			//uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeMaskWriteRegister &&
			//uint16(jsonPayload["FunctionCode"].(float64)) != modbus.FuncCodeReadFIFOQueue {

			log.Println("[ERROR] handleRequest - FunctionCode specified in incoming payload is invalid")
			addErrorToPayload(jsonPayload, "Invalid FunctionCode", modbus.ExceptionCodeIllegalFunction)
			jsonPayload["request"] = payload
		}
	}

	if jsonPayload["StartAddress"] == nil {
		log.Println("[ERROR] handleRequest - StartAddress not specified in incoming payload")
		addErrorToPayload(jsonPayload, "StartAddress is required", errorCode)
		jsonPayload["request"] = payload
	}

	if jsonPayload["AddressCount"] == nil &&
		(uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeReadDiscreteInputs ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeReadCoils ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeWriteMultipleCoils ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeReadInputRegisters ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeReadHoldingRegisters ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeWriteMultipleRegisters ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeReadWriteMultipleRegisters) {
		log.Println("[ERROR] handleRequest - AddressCount not specified in incoming payload and is required for the specified function code.")
		addErrorToPayload(jsonPayload, "AddressCount is required", errorCode)
		jsonPayload["request"] = payload
	}

	if jsonPayload["Data"] == nil &&
		(uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeWriteSingleCoil ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeWriteMultipleCoils ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeWriteSingleRegister ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeWriteMultipleRegisters ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeMaskWriteRegister ||
			uint16(jsonPayload["FunctionCode"].(float64)) == modbus.FuncCodeReadWriteMultipleRegisters) {
		log.Println("[ERROR] handleRequest - Data not specified in incoming payload and is required for the specified function code.")
		addErrorToPayload(jsonPayload, "Data is required for 'write' function codes", errorCode)
		jsonPayload["request"] = payload
	}

	if jsonPayload["error"] == nil {
		err := handleModbusRequest(jsonPayload)

		log.Printf("[DEBUG] handleRequest - err = %#v\n", err)
		log.Printf("[DEBUG] handleRequest - jsonPayload = %#v\n", jsonPayload)

		if err != nil {
			log.Printf("[ERROR] handleRequest - Error encountered: %s\n", err.Error())
			switch err.(type) {
			case *net.OpError:
				log.Printf("[DEBUG] handleRequest - net.OpError received\n")
				//We have a network issue. At this point, we need to continually try and reconnect.
				modbusHandler.Address = ""
			case *modbus.ModbusError:
				log.Printf("[DEBUG] handleRequest - modbus.ModbusError received:  %#v\n", err)
				//extract the modbus exception code
				errorCode = int(err.(*modbus.ModbusError).ExceptionCode)
				log.Printf("[DEBUG] handleRequest - modbus exception code = %d\n", errorCode)
			}
			addErrorToPayload(jsonPayload, err.Error(), errorCode)
		} else {
			if jsonPayload["success"] == nil {
				jsonPayload["success"] = true
			}
		}
	}

	log.Println("[INFO] handleRequest - publishing response")
	publishModbusResponse(jsonPayload)
}

func handleModbusRequest(payload map[string]interface{}) error {
	// Modbus TCP
	var modbusResults []byte
	var err error

	//See if the modbus address changed
	if modbusHandler.Address != payload["ModbusHost"] {
		log.Println("[INFO] handleModbusRequest - Modbus host address modified. Resetting Modbus Client")
		if err := resetModbusClient(payload["ModbusHost"].(string)); err != nil {
			return err
		}
	}

	functionCode := int(payload["FunctionCode"].(float64))
	startAddress := uint16(payload["StartAddress"].(float64))
	addressCount := uint16(payload["AddressCount"].(float64))

	log.Printf("[DEBUG] handleModbusRequest - function code = %d\n", functionCode)
	log.Printf("[DEBUG] handleModbusRequest - start address = %d\n", startAddress)
	log.Printf("[DEBUG] handleModbusRequest - address count = %d\n", addressCount)

	switch functionCode {
	case modbus.FuncCodeReadDiscreteInputs:
		log.Println("[DEBUG] handleModbusRequest - invoking ReadDiscreteInputs")
		modbusResults, err = modbusClient.ReadDiscreteInputs(startAddress, addressCount)
	case modbus.FuncCodeReadCoils:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeReadCoils")
		modbusResults, err = modbusClient.ReadCoils(startAddress, addressCount)
	case modbus.FuncCodeWriteSingleCoil:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeWriteSingleCoil")
		var modbusData uint16 = 0x0000

		// switch payload["Data"].([]interface{})[0].(type) {
		// case float64:
		// 	if payload["Data"].([]interface{})[0].(float64) == 1 {
		// 		modbusData = 0xFF00
		// 	}
		// case bool:
		// 	if payload["Data"].([]interface{})[0].(bool) == true {
		// 		modbusData = 0xFF00
		// 	}
		switch payload["Data"].(interface{}).(type) {
		case float64:
			if payload["Data"].(interface{}).(float64) == 1 {
				modbusData = 0xFF00
			}
		case bool:
			if payload["Data"].(interface{}).(bool) == true {
				modbusData = 0xFF00
			}
		default:
			log.Println("[ERROR] handleModbusRequest - Invalid data value passed for function code")
		}

		modbusResults, err = modbusClient.WriteSingleCoil(startAddress, modbusData)
	case modbus.FuncCodeWriteMultipleCoils:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeWriteMultipleCoils")
		modbusResults, err = modbusClient.WriteMultipleCoils(startAddress, addressCount, translateDataToModbusBytes(functionCode, payload["Data"].([]bool)))
	case modbus.FuncCodeReadInputRegisters:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeReadInputRegisters")
		modbusResults, err = modbusClient.ReadInputRegisters(startAddress, addressCount)
	case modbus.FuncCodeReadHoldingRegisters:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeReadHoldingRegisters")
		modbusResults, err = modbusClient.ReadHoldingRegisters(startAddress, addressCount)
	case modbus.FuncCodeWriteSingleRegister:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeWriteSingleRegister")
		modbusResults, err = modbusClient.WriteSingleRegister(startAddress, uint16(payload["Data"].(float64)))
	case modbus.FuncCodeWriteMultipleRegisters:
		log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeWriteMultipleRegisters")
		modbusResults, err = modbusClient.WriteMultipleRegisters(startAddress, addressCount, payload["Data"].([]byte))
		//case modbus.FuncCodeReadWriteMultipleRegisters:
		//	log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeReadWriteMultipleRegisters")
		//	modbusResults, err = client.ReadWriteMultipleRegisters(startAddress, payload["AddressCount"].(uint16),)
		//case modbus.FuncCodeMaskWriteRegister:
		//	log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeMaskWriteRegister")
		//	modbusResults, err = client.MaskWriteRegister(startAddress)
		//case modbus.FuncCodeReadFIFOQueue:
		//	log.Println("[DEBUG] handleModbusRequest - invoking FuncCodeReadFIFOQueue")
		//	modbusResults, err = client.ReadFIFOQueue(startAddress)
	}

	log.Printf("[DEBUG] modbusResults = %#v\n", modbusResults)

	if err != nil {
		return err
	}

	log.Printf("[DEBUG] function code = %d\n", functionCode)

	switch functionCode {
	case modbus.FuncCodeReadDiscreteInputs,
		modbus.FuncCodeReadCoils, modbus.FuncCodeWriteSingleCoil, modbus.FuncCodeWriteMultipleCoils:
		log.Printf("[DEBUG] handleModbusRequest - adding results to Data field in payload: %#v\n", modbusResults)
		payload["Data"] = translateModbusBytesToData(modbusResults, addressCount)

		log.Printf("[DEBUG] payload.Data set, payload = %#v\n", payload)
	default:
		log.Printf("[DEBUG] handleModbusRequest - adding default bytes to data field in payload: %#v\n", modbusResults)
		var data []uint16
		for x := uint16(0); x < addressCount; x++ {
			data = append(data, binary.BigEndian.Uint16(modbusResults[x*2:(x*2)+2]))
		}
		payload["Data"] = data
	}

	log.Printf("[DEBUG] returning payload, payload = %#v\n", payload)

	return nil
}

func addErrorToPayload(payload map[string]interface{}, errMsg string, errCode int) {
	payload["success"] = false
	payload["error"] = make(map[string]interface{})

	payload["error"].(map[string]interface{})["code"] = errCode

	if errMsg != "" {
		payload["error"].(map[string]interface{})["message"] = errMsg
	}
}

// Subscribes to a topic
func subscribe(topic string) (<-chan *mqttTypes.Publish, error) {
	log.Printf("[DEBUG] subscribe - Subscribing to topic %s\n", topic)
	subscription, error := cbBroker.client.Subscribe(topic, cbBroker.qos)
	if error != nil {
		log.Printf("[ERROR] subscribe - Unable to subscribe to topic: %s due to error: %s\n", topic, error.Error())
		return nil, error
	}

	log.Printf("[DEBUG] subscribe - Successfully subscribed to = %s\n", topic)
	return subscription, nil
}

// Publishes data to a topic
func publish(topic string, data string) error {
	log.Printf("[DEBUG] publish - Publishing to topic %s\n", topic)
	error := cbBroker.client.Publish(topic, []byte(data), cbBroker.qos)
	if error != nil {
		log.Printf("[ERROR] publish - Unable to publish to topic: %s due to error: %s\n", topic, error.Error())
		return error
	}

	log.Printf("[DEBUG] publish - Successfully published message to = %s\n", topic)
	return nil
}

func getAdapterConfig() {
	log.Println("[INFO] getAdapterConfig - Retrieving adapter config")

	//Retrieve the adapter configuration row
	query := cb.NewQuery()
	query.EqualTo("adapter_name", "modbusClientAdapter")

	//A nil query results in all rows being returned
	log.Println("[DEBUG] getAdapterConfig - Executing query against table " + adapterConfigCollection)
	results, err := cbBroker.client.GetDataByName(adapterConfigCollection, query)
	if err != nil {
		log.Println("[DEBUG] getAdapterConfig - Adapter configuration could not be retrieved. Using defaults")
		log.Printf("[DEBUG] getAdapterConfig - Error: %s\n", err.Error())
	} else {
		if len(results["DATA"].([]interface{})) > 0 {
			log.Printf("[DEBUG] getAdapterConfig - Adapter config retrieved: %#v\n", results)
			log.Println("[INFO] getAdapterConfig - Adapter config retrieved")

			//topic root
			if results["DATA"].([]interface{})[0].(map[string]interface{})["topic_root"] != nil {
				log.Printf("[DEBUG] getAdapterConfig - Setting topicRoot to %s\n", results["DATA"].([]interface{})[0].(map[string]interface{})["topic_root"].(string))
				topicRoot = results["DATA"].([]interface{})[0].(map[string]interface{})["topic_root"].(string)
			} else {
				log.Printf("[DEBUG] getAdapterConfig - Topic root is nil. Using default value %s\n", topicRoot)
			}
		} else {
			log.Println("[DEBUG] getAdapterConfig - No rows returned. Using defaults")
		}
	}
}

func publishModbusResponse(respJson map[string]interface{}) {
	//Create the response topic
	var theTopic string
	if respJson["error"] != nil {
		theTopic = topicRoot + "/error"
	} else {
		theTopic = topicRoot + "/response"
	}

	//Add a timestamp to the payload
	respJson["timestamp"] = time.Now().Format(JavascriptISOString)

	// // TODO Add custom key for adapterID, defaulting to rail context, SiteID
	// if adapterID != "" {
	// 	respJson["SiteID"] = adapterID
	// }

	respStr, err := json.Marshal(respJson)
	if err != nil {
		log.Printf("[ERROR] publishModbusResponse - ERROR marshalling json response: %s\n", err.Error())
	} else {
		log.Printf("[DEBUG] publishModbusResponse - Publishing response %s to topic %s\n", string(respStr), theTopic)

		//Publish the response
		err = publish(theTopic, string(respStr))
		if err != nil {
			log.Printf("[ERROR] publishModbusResponse - ERROR publishing to topic: %s\n", err.Error())
		}
	}
}

func translateDataToModbusBytes(functionCode int, data []bool) []byte {
	//We need to take the individual boolean values provided in the write multiple coils
	//function code and create bytes according to the modbus spec.
	var returnData []byte
	var mask byte

	for ndx, theBool := range data {
		if ndx%8 == 0 {
			if ndx > 0 {
				returnData = append(returnData, mask)
			}
			mask = 0
		}
		mask = mask << 1

		if theBool == true {
			mask = mask | 1
		}
	}

	return returnData
}

func translateModbusBytesToData(modbusBytes []byte, addressCount uint16) []bool {
	//We need to take the bytes returned from the read coils and read discrete input
	//function codes and create boolean arrays
	//The modbus spec dictates that each byte contains the coil/discrete input values
	//for 8 consective addresses
	//
	//If the address count is not a multiple of 8, the highest significant bits in the last
	//byte returned will be set to zero
	returnData := make([]bool, addressCount)

	for ndx, theByte := range modbusBytes {

		mask := theByte
		addrNdx := (ndx * 8)
		for bitIndex := 0; bitIndex < 8 && bitIndex+addrNdx < int(addressCount); bitIndex++ {
			returnData[addrNdx+bitIndex] = false
			if mask&0x01 == 1 {
				returnData[addrNdx+bitIndex] = true
			}
			mask = mask >> 1
		}
	}

	return returnData
}
