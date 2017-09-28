'''
cbModbus cbData
-----------------

A collection of utility functions for retrieving data from and writing data to the Modbus data
collections defined within the ClearBlade Platform.
'''
import logging
from clearblade.ClearBladeCore import Query

MODBUS_DATA_COLLECTIONS = {
    'COILS_COLLECTION': "Discrete_Output_Coils",
    'CONTACTS_COLLECTION': "Discrete_Input_Contacts",
    'INPUT_REGISTERS_COLLECTION': "Analog_Input_Registers",
    'OUTPUT_REGISTERS_COLLECTION': "Analog_Output_Holding_Registers"
}


def validate_coil_address(cbsystem, cbauth, slave, address, count):
    """Query the Discrete_Output_Coils collection to see if all of the addresses exist

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: validate_address Function invocation
    '''
    """
    logging.debug("Begin validate_coil_address")
    return validate_address(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['COILS_COLLECTION'])

def validate_discrete_input_address(cbsystem, cbauth, slave, address, count):
    """Query the Discrete_Input_Contacts collection to see if all of the addresses exist

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: validate_address Function invocation
    """
    logging.debug("Begin validate_coil_address")
    return validate_address(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['CONTACTS_COLLECTION'])

def validate_holding_reg_address(cbsystem, cbauth, slave, address, count):
    """Query the Analog_Output_Holding_Registers collection to see if all of the addresses exist

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: validate_address Function invocation
    """
    logging.debug("Begin validate_coil_address")
    return validate_address(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['OUTPUT_REGISTERS_COLLECTION'])

def validate_input_reg_address(cbsystem, cbauth, slave, address, count):
    """Query the Analog_Input_Registers collection to see if all of the addresses exist

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: validate_address Function invocation
    """
    logging.debug("Begin validate_coil_address")
    return validate_address(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['INPUT_REGISTERS_COLLECTION'])

def validate_address(cbsystem, cbauth, slave, address, count, collection):
    """Query the specified collection to see if all of the addresses exist

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: True if all addresses for a specific slave exist, False otherwise.
    """
    logging.debug("Begin validate_address")
    logging.debug("Slave = %s", slave)
    logging.debug("Address = %s", address)
    logging.debug("Count = %s", count)

    rows = read_collection_data(cbsystem, cbauth, slave, address, count, collection)

    # See if there are any addresses missing
    if len(rows) < count:
        logging.debug("validate_address-read_collection_data: ADDRESSES MISSING")
        return False
    else:
        logging.debug("validate_address-read_collection_data: ALL ADDRESSES FOUND")
        return True

def read_coils(cbsystem, cbauth, slave, address, count):
    """Retrieve coil values from the Discrete_Output_Coils collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: read_modbus_data Function invocation
    """
    logging.debug("Begin read_coils")

    rows = read_modbus_data(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['COILS_COLLECTION'])
    return rows


def read_discrete_inputs(cbsystem, cbauth, slave, address, count):
    """Retrieve contact values from the Discrete_Input_Contacts collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: read_modbus_data Function invocation
    """
    logging.debug("Begin read_coils")

    rows = read_modbus_data(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['CONTACTS_COLLECTION'])
    return rows


def read_holding_registers(cbsystem, cbauth, slave, address, count):
    """Retrieve output register values from the Analog_Output_Holding_Registers collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: read_modbus_data Function invocation
    """
    logging.debug("Begin read_coils")

    rows = read_modbus_data(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['OUTPUT_REGISTERS_COLLECTION'])
    return rows


def read_input_registers(cbsystem, cbauth, slave, address, count):
    """Retrieve input register values from the Analog_Input_Registers collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve

    :returns: read_modbus_data Function invocation
    """
    logging.debug("Begin read_coils")

    rows = read_modbus_data(cbsystem, cbauth, slave, address, count, \
        MODBUS_DATA_COLLECTIONS['INPUT_REGISTERS_COLLECTION'])
    return rows

def read_modbus_data(cbsystem, cbauth, slave, address, count, collection):
    """Retrieve Modbus data values for specified addresses from a named collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve
    :param collection: The name of the ClearBlade platform data collection in which to query

    :returns: Array of Modbus data values
    """
    rows = read_collection_data(cbsystem, cbauth, slave, address, count, collection)

    #Return data needs to be in an array
    values = []
    for row in rows:
        values.append(row["data_value"])

    return values


def read_collection_data(cbsystem, cbauth, slave, address, count, collection):
    """Retrieve data from the specified collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param count: The number of values to retrieve
    :param collection: The name of the ClearBlade platform data collection in which to query

    :returns: Rows from the named data collection associated with the specified slave and data
              addresses
    """
    logging.debug("Begin read_collection_data")

    collection = cbsystem.Collection(cbauth, collectionName=collection)

    the_query = Query()
    the_query.equalTo("unit_id", slave)

    if count > 1:
        the_query.greaterThanEqualTo("data_address", address)
        the_query.lessThan("data_address", address+count)
    else:
        the_query.equalTo("data_address", address)

    return collection.getItems(the_query)

def write_coils(cbsystem, cbauth, slave, address, data):
    """Save coil values into the Discrete_Output_Coils collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param data: The data values to write to the Discrete_Output_Coils collection
    """
    logging.debug("Begin write_coils")
    write_collection_data(cbsystem, cbauth, slave, address, data, \
        MODBUS_DATA_COLLECTIONS['COILS_COLLECTION'])


def write_holding_registers(cbsystem, cbauth, slave, address, data):
    """Save register values into the Analog_Output_Holding_Registers collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param data: The data values to write to the Analog_Output_Holding_Registers collection
    """
    logging.debug("Begin write_holding_registers")
    write_collection_data(cbsystem, cbauth, slave, address, data, \
        MODBUS_DATA_COLLECTIONS['OUTPUT_REGISTERS_COLLECTION'])

def write_collection_data(cbsystem, cbauth, slave, address, data, collection):
    """Retrieve input register values from the Analog_Input_Registers collection

    :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                     will communicate with.
    :param cbauth: The object representing the ClearBlade Platform authentication credentials.
    :param slave: The unit id of the modbus device validation should be performed against.
    :param address: The starting address
    :param data: The data values to write to the Analog_Output_Holding_Registers collection
    :param collection: The name of the ClearBlade platform data collection in which to write
                        the data to
    """
    logging.debug("Begin write_collection_data")

    collection = cbsystem.Collection(cbauth, collectionName=collection)

    for ndx in range(0, len(data)):

        the_query = Query()
        the_query.equalTo("unit_id", slave)
        the_query.equalTo("data_address", address + ndx)

        collection.updateItems(the_query, {"data_value": data[ndx]})
