'''
cbModbus mqtt
-----------------

A collection of objects to encapsulate mqtt topic values

MODBUS Command structure

{
    'ModbusHost': host,
    'ModbusPort': port,
    'FunctionCode': int,
    'UnitID': int,
    'Address': int,
    'ZeroMode': true|false,
    'Data': []
}
'''

import logging

MODBUS_CLIENT_TOPICS = {
    'MODBUS_REQUEST': "modbus/command/request",
    'MODBUS_RESPONSE': "modbus/command/response",
    'MODBUS_ERROR': "modbus/command/error"
}

def create_topic(topic_root, sub_topic):
    '''Create a topic by appending the sub_topic to the topic_root'''
    topic = ""

    logging.debug("Creating message topic. Topic root = %s, sub_topic = %s", \
        topic_root, sub_topic)
    if topic_root != "":
        topic = topic_root

        if not topic_root.endswith('/') and not sub_topic.startswith('/'):
            topic += '/'

    logging.debug("Returning topic %s", topic + sub_topic)

    return topic + sub_topic

def publish_modbus_error(mqtt_client, topic_root, error):
    '''Publish a modbus error to the ClearBlade Platform'''
    logging.debug("Publishing Modbus error: %s", error)
    mqtt_client.publish(create_topic(topic_root, MODBUS_CLIENT_TOPICS['MODBUS_ERROR']), str(error))


def publish_modbus_response(mqtt_client, topic_root, resp):
    '''Publish a modbus response to the ClearBlade Platform'''
    logging.debug("Publishing Modbus response: %s", resp)
    mqtt_client.publish(create_topic(topic_root, MODBUS_CLIENT_TOPICS['MODBUS_RESPONSE']), \
        str(resp))
