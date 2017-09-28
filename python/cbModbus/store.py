'''
cbModbus store
-----------------

A class representing a Modbus datastore which integrates with a ClearBlade Platform.
'''
import logging
from cbModbus import cbData
from cbModbus.constants import ModbusFunctionCodes, ModbusErrorCodes
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.exceptions import ParameterException

class CbModbusDatastore(BaseModbusDataBlock):
    ''' A modbus datastore integrated with the ClearBlade Platform '''

    def __init__(self, cbsystem, cbauth):
        ''' Initializes the datastore

        :param cbsystem: The ClearBlade system object representing the ClearBlade System the adapter
                         will communicate with.
        :param cbauth:   The object representing the ClearBlade Platform authentication credentials.
        '''
        self.cbsystem = cbsystem
        self.cbauth = cbauth

    def validate(self, slave, fx, address, count=1):
        ''' Checks to see if the request is in range

        :param address: The starting address
        :param count: The number of values to test for

        :returns: True if the request is within range, False otherwise
        '''
        logging.debug("In CbModbusDatastore.validate")

        if fx == ModbusFunctionCodes.ReadCoil or \
            fx == ModbusFunctionCodes.WriteSingleCoil or \
            fx == ModbusFunctionCodes.WriteMultipleCoils:

            return cbData.validate_coil_address(self.cbsystem, self.cbauth, slave, address, count)
        elif fx == ModbusFunctionCodes.ReadDiscreteInput:
            return cbData.validate_discrete_input_address(self.cbsystem, self.cbauth, slave, \
                address, count)
        elif fx == ModbusFunctionCodes.ReadHoldingRegisters or \
            fx == ModbusFunctionCodes.WriteSingleHoldingRegister or \
            fx == ModbusFunctionCodes.WriteMultipleHoldingRegisters:

            return cbData.validate_holding_reg_address(self.cbsystem, self.cbauth, slave, \
                    address, count)
        elif fx == ModbusFunctionCodes.ReadInputRegisters:
            return cbData.validate_input_reg_address(self.cbsystem, self.cbauth, slave, \
                    address, count)
        else:
            raise ParameterException("Invalid function code received for \
                CbModbusDatastore.validate request. Function code received = " + str(fx))

        return True

    def getValues(self, slave, fx, address, count=1):
        ''' Returns the requested values of the datastore

        :param address: The starting address
        :param count: The number of values to retrieve

        :returns: The requested values from a:a+c
        '''
        logging.debug("In CbModbusDatastore.getValues")

        if fx == ModbusFunctionCodes.ReadCoil or \
            fx == ModbusFunctionCodes.WriteSingleCoil or \
            fx == ModbusFunctionCodes.WriteMultipleCoils:

            return cbData.read_coils(self.cbsystem, self.cbauth, slave, address, count)
        elif fx == ModbusFunctionCodes.ReadDiscreteInput:
            return cbData.read_discrete_inputs(self.cbsystem, self.cbauth, slave, address, count)
        elif fx == ModbusFunctionCodes.ReadHoldingRegisters or \
            fx == ModbusFunctionCodes.WriteSingleHoldingRegister or \
            fx == ModbusFunctionCodes.WriteMultipleHoldingRegisters:

            return cbData.read_holding_registers(self.cbsystem, self.cbauth, slave, address, count)
        elif fx == ModbusFunctionCodes.ReadInputRegisters:
            return cbData.read_input_registers(self.cbsystem, self.cbauth, slave, address, count)
        else:
            raise ParameterException("Invalid function code received for \
                CbModbusDatastore.getValues request. Function code received = " + str(fx))

    def setValues(self, slave, fx, address, values):
        ''' Sets the requested values of the datastore

        :param address: The starting address
        :param values: The new values to be set
        '''
        logging.debug("In CbModbusDatastore.setValues")

        if fx == ModbusFunctionCodes.WriteSingleCoil or \
            fx == ModbusFunctionCodes.WriteMultipleCoils:

            cbData.write_coils(self.cbsystem, self.cbauth, slave, address, values)
        elif fx == ModbusFunctionCodes.WriteSingleHoldingRegister or \
            fx == ModbusFunctionCodes.WriteMultipleHoldingRegisters:

            cbData.write_holding_registers(self.cbsystem, self.cbauth, slave, address, values)
        else:
            raise ParameterException("Invalid function code received for \
                CbModbusDatastore.setValues request.  Function code received = " + str(fx))
