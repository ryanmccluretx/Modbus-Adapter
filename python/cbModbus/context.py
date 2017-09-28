#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
import logging

from cbModbus.store import CbModbusDatastore
from pymodbus.constants import Defaults
from pymodbus.exceptions import NoSuchSlaveException
from pymodbus.interfaces import IModbusSlaveContext

#---------------------------------------------------------------------------#
# Slave Datastore Contexts
#---------------------------------------------------------------------------#
class ClearBladeModbusSlaveContext(IModbusSlaveContext):
    '''
    A modbus slave context. Represents a specific slave.

    :param zero_mode:   The zero_mode of the slave. zero_mode means that a
                        request to address(0-7) will map to the address (0-7). The default is
                        False which is based on section 4.4 of the specification, so address(0-7)
                        will map to the address (1-8)
    :param slave:       The unit id associated with the slave/server.abs
    :param cbsystem:    The ClearBlade system object representing the ClearBlade System the adapter
                        will communicate with.
    :param cbauth:      The object representing the ClearBlade Platform authentication credentials.
    '''
    def __init__(self, **kwargs):
        self.zero_mode = kwargs.get('zero_mode', Defaults.ZeroMode)
        self.unit_id = kwargs.get('slave', 0)
        self.store = CbModbusDatastore(cbsystem=kwargs.get('cbsystem', None), \
            cbauth=kwargs.get('cbauth', None))

    def __str__(self):
        ''' Returns a string representation of the context

        :returns: A string representation of the context
        '''
        return "ClearBlade Modbus Slave Context"

    def reset(self):
        ''' Resets all the datastores to their default values '''
        #Noop for this implementation
        logging.debug("In ClearBladeModbusSlaveContext.reset")

    def validate(self, fx, address, count=1):
        ''' Validates the request to make sure it is in range

        :param fx: The function we are working with
        :param address: The starting address
        :param count: The number of values to test
        :returns: True if the request in within range, False otherwise
        '''

        logging.debug("In ClearBladeModbusSlaveContext.validate")
        if not self.zero_mode:
            address = address + 1
        logging.debug("validate[%d] %d:%d", fx, address, count)
        return self.store.validate(self.unit_id, fx, address, count)

    def getValues(self, fx, address, count=1):
        ''' Validates the request to make sure it is in range

        :param fx: The function we are working with
        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from address:address+count
        '''
        logging.debug("In ClearBladeModbusSlaveContext.getValues")

        if not self.zero_mode:
            address = address + 1
        logging.debug("getValues[%d] %d:%d", fx, address, count)
        return self.store.getValues(self.unit_id, fx, address, count)

    def setValues(self, fx, address, values):
        ''' Sets the datastore with the supplied values

        :param fx: The function we are working with
        :param address: The starting address
        :param values: The new values to be set
        '''
        logging.debug("In ClearBladeModbusSlaveContext.setValues")
        if not self.zero_mode:
            address = address + 1

        logging.debug("setValues[%d] %d:%d", fx, address, len(values))
        self.store.setValues(self.unit_id, fx, address, values)

class ClearBladeModbusServerContext(object):
    '''
    A modbus server context.

    :param zero_mode:   The zero_mode of the slave. zero_mode means that a
                        request to address(0-7) will map to the address (0-7). The default is
                        False which is based on section 4.4 of the specification, so address(0-7)
                        will map to the address (1-8)
    :param cbsystem:    The ClearBlade system object representing the ClearBlade System the adapter
                        will communicate with.
    :param cbauth:      The object representing the ClearBlade Platform authentication credentials.
    '''

    def __init__(self, **kwargs):
        ''' Initializes a new instance of a server context.

        :param cbsystem:  The ClearBlade system object representing the ClearBlade System the adapter
                          will communicate with.
        :param cbauth:    The object representing the ClearBlade Platform authentication credentials.
        :param zero_mode: Set to true to treat this as a single context
        '''

        self.cbauth = kwargs.get('cbauth', None)
        self.cbsystem = kwargs.get('cbsystem', None)
        self.zero_mode = kwargs.get('zero_mode', Defaults.ZeroMode)
        self.store = CbModbusDatastore(cbsystem=self.cbsystem, cbauth=self.cbauth)

    def __contains__(self, slave):
        ''' Check if the given slave exists

        :param slave: slave The slave to check for existance
        :returns: True if the slave exists, False otherwise
        '''
        logging.debug("In ClearBladeModbusServerContext.__contains__")

        #TODO Query the CB platform to see if the slave exists
        return True

    def __getitem__(self, slave):
        ''' Used to get access to a slave context

        :param slave: The slave context to get
        :returns: The requested slave context
        '''
        logging.debug("In ClearBladeModbusServerContext.__getitem__")

        return ClearBladeModbusSlaveContext(cbauth=self.cbauth,
                                            cbsystem=self.cbsystem,
                                            zero_mode=self.zero_mode,
                                            slave=slave)
