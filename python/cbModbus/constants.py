'''
Constants For Modbus Server/Client
----------------------------------

This is the single location for storing default
values for the servers and clients.
'''
from pymodbus.interfaces import Singleton

class ModbusFunctionCodes(Singleton):
    ''' Represents the Modbus Function Code Values

    .. attribute:: ReadCoil

       Function code 1 - Modbus Read Coil function.

    .. attribute:: ReadDiscreteInput

       Function code 2 - Modbus Read Discrete Input function.
    
    .. attribute:: ReadHoldingRegisters

       Function code 3 - Modbus Read Holding Registers function.
    
    .. attribute:: ReadInputRegisters

       Function code 4 - Modbus Read Input Registers function.
    
    .. attribute:: WriteSingleCoil

       Function code 5 - Modbus Write Single Coil function.

    .. attribute:: WriteSingleHoldingRegister

       Function code 6 - Modbus Write Single Coil function.

    .. attribute:: WriteMultipleCoils

       Function code 15 - Modbus Write Single Coil function.

    .. attribute:: WriteMultipleHoldingRegisters

       Function code 16 - Modbus Write Single Coil function.
    '''
    ReadCoil = 1
    ReadDiscreteInput = 2
    ReadHoldingRegisters = 3
    ReadInputRegisters = 4
    WriteSingleCoil = 5
    WriteSingleHoldingRegister = 6
    WriteMultipleCoils = 15
    WriteMultipleHoldingRegisters = 16

class ModbusErrorCodes(Singleton):
    ''' Represents the Modbus Error Code Values

    .. attribute:: IllegalFunction

       Error code 1 - Modbus Illegal Function error.
       The function code received in the query is not recognized by the slave or is not allowed by the slave.

    .. attribute:: IllegalDataAddress

       Error code 2 - Modbus Illegal Data Address error.
       The data address (register number) received in the query is not an allowed address for the slave, i.e., the register does not exist. If multiple registers were requested, at least one was not permitted.

    .. attribute:: IllegalDataValue

       Error code 3 - Illegal Data Value error.
       The value contained in the query's data field is not acceptable to the slave.

    .. attribute:: SlaveDeviceFailure

       Error code 4 - Slave Device Failure error.
       An unrecoverable error occurred while the slave was attempting to perform the requested action.
 
    .. attribute:: SlaveDeviceBusy

       Error code 6 - Slave Device Busy error.
       The slave is engaged in processing a long-duration command. The master should try again later.
 
    .. attribute:: GatewayPathUnavailable

       Error code 10 - Gateway Path Unavailable error.
       Specialized use in conjunction with gateways, usually means the gateway is misconfigured or overloaded

    .. attribute:: GatewayDeviceFailedtoRespond

       Error code 11 - Gateway Target Device Failed to Respond error.
       Specialized use in conjunction with gateways, indicates no response was received from the target device. 
    '''
    IllegalFunction = 1
    IllegalDataAddress = 2
    IllegalDataValue = 3
    SlaveDeviceFailure = 4
    SlaveDeviceBusy = 6
    GatewayPathUnavailable = 10
    GatewayDeviceFailedtoRespond = 11