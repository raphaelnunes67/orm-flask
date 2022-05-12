import asyncio
import os
import time

from pymodbus.client.asynchronous import schedulers
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder

from services.api_requests import ApiRequests
from services.models import ModelInfo, Dut
from services.tools import Tools


class Monitor(object):

    def __init__(self, mbus_client, settings, logger):
        self.client = mbus_client.protocol
        self.logger = logger
        self.settings = settings
        self.ng_list = []
        self.requests = ApiRequests(settings=self.settings)

    @staticmethod
    def convert_to_string(registers: list):
        return bytes(sum([[element & 0xFF, (element >> 8) & 0xFF] for element in registers], [])).decode('utf-8')

    @staticmethod
    def convert_to_int(registers: list):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder='>', wordorder='<').decode_32bit_int()

    async def process_dut(self, dut: Dut):
        if self.requests.send_dut_info(dut):
            self.logger.debug('async_clp_pooling - API request success')
        else:
            self.logger.exception('async_clp_pooling - API request failed')

        if dut.result != 15:
            self.ng_list.append(dut)
            # result = bin(dut.result)[2:]
            # values = list(result)
            # await self.client.write_coil(settings['modbustcp']['coils']['ng_01']['scanner'], True)
            # await self.client.write_coil(settings['modbustcp']['coils']['ng_01']['width'], False)
            # await self.client.write_coil(settings['modbustcp']['coils']['ng_01']['length'], False)
            # await self.client.write_coil(settings['modbustcp']['coils']['ng_01']['thickness'], True)

    async def run(self):
        self.logger.debug("async_clp_pooling - starting")
        loop_delay = 1 / settings['modbustcp']['pooling_freq']
        connection_notified = False
        disconnection_notified = False
        prev_status = 0
        update_model = True  # first time get model selected on the machine..
        get_qr_code = False
        model = ''
        exceptions_counter = 0
        model_info = ModelInfo()

        while True:
            if self.client and self.client.connected:
                try:
                    if update_model:
                        update_model = False

                        # request model name
                        rq = await self.client.read_holding_registers(
                            address=settings['modbustcp']['read_regs']['model']['position'],
                            count=settings['modbustcp']['read_regs']['model']['size']
                        )
                        model_info.name = self.convert_to_string(rq.registers)

                        # request model width
                        rq = await self.client.read_holding_registers(
                            address=settings['modbustcp']['read_regs']['model_width']['position'],
                            count=settings['modbustcp']['read_regs']['model_width']['size']
                        )
                        model_info.width_max = self.convert_to_int(rq.registers[0:2]) / 1000
                        model_info.width = self.convert_to_int(rq.registers[2:4]) / 1000
                        model_info.width_min = self.convert_to_int(rq.registers[4:6]) / 1000
                        model_info.torque_1 = self.convert_to_int(rq.registers[6:8]) / 100

                        # request model length
                        rq = await self.client.read_holding_registers(
                            address=settings['modbustcp']['read_regs']['model_length']['position'],
                            count=settings['modbustcp']['read_regs']['model_length']['size']
                        )
                        model_info.length_max = self.convert_to_int(rq.registers[0:2]) / 1000
                        model_info.length = self.convert_to_int(rq.registers[2:4]) / 1000
                        model_info.length_min = self.convert_to_int(rq.registers[4:6]) / 1000
                        model_info.torque_2 = self.convert_to_int(rq.registers[6:8]) / 100

                        # request model thickness
                        rq = await self.client.read_holding_registers(
                            address=settings['modbustcp']['read_regs']['model_thickness']['position'],
                            count=settings['modbustcp']['read_regs']['model_thickness']['size']
                        )
                        model_info.thickness_max = self.convert_to_int(rq.registers[0:2]) / 1000
                        model_info.thickness = self.convert_to_int(rq.registers[2:4]) / 1000
                        model_info.thickness_min = self.convert_to_int(rq.registers[4:6]) / 1000
                        model_info.torque_3 = self.convert_to_int(rq.registers[6:8]) / 100

                    rq = await self.client.read_coils(settings['modbustcp']['coils']['test_end'])
                    test_end = rq.bits[0]
                    if test_end:
                        await self.client.write_coil(settings['modbustcp']['coils']['test_end'], False)

                        # request qr code
                        rq = await self.client.read_holding_registers(
                            address=settings['modbustcp']['read_regs']['qr_code']['position'],
                            count=settings['modbustcp']['read_regs']['qr_code']['size']
                        )

                        qr_value = self.convert_to_string(rq.registers)

                        # request test result
                        rq = await self.client.read_holding_registers(
                            address=settings['modbustcp']['read_regs']['result']['position'],
                            count=settings['modbustcp']['read_regs']['result']['size']
                        )

                        self.logger.debug("async_clp_pooling - test end - serial number: {}".format(qr_value))

                        dut = Dut()
                        dut.model_info = model_info
                        dut.qr_code = qr_value
                        dut.width = self.convert_to_int(rq.registers[0:2]) / 10000
                        dut.length = self.convert_to_int(rq.registers[2:4]) / 10000
                        dut.thickness = self.convert_to_int(rq.registers[4:6]) / 10000
                        dut.result = rq.registers[6]

                        await self.process_dut(dut)

                    #  todo: notify backend or turn on LED indicating that the CLP is connected
                    # if not connection_notified:
                    #     connection_notified = True
                    #     disconnection_notified = False
                    # exceptions_counter = 0
                except AttributeError as e:
                    self.logger.exception('async_clp_pooling AttributeError exception: {}'.format(repr(e)))
                    if not disconnection_notified:
                        #  todo: notify backend that the CLP is DISconnected
                        disconnection_notified = True
                        connection_notified = False
                        self.client.connected = False
                except Exception as e:
                    if exceptions_counter < 30:
                        exceptions_counter += 1
                    self.logger.exception('async_clp_pooling exception: {}'.format(repr(e)))
                    time.sleep(exceptions_counter)
            else:
                time.sleep(exceptions_counter)
                self.logger.debug("waiting for connection..")
                if not disconnection_notified:
                    #  todo: notify backend that the CLP is DISconnected
                    disconnection_notified = True
                    connection_notified = False
            await asyncio.sleep(loop_delay)


if __name__ == '__main__':
    # Create a TCP/IP socket
    tools = Tools()
    env = os.environ.get('SISBAT_SETTINGS', 'dev')
    if env == 'dev':
        logger = tools.get_stdout_logger('CLP')
    else:
        logger = tools.get_logger(logger_name='CLP', path=tools.logs_path + '/CLP.log')
    settings = tools.get_settings(file_path=tools.settings_path + '/clp_monitor.yml')

    # check if debug server should be run
    debug = int(os.environ.get('SISBAT_DEBUGGER', 0))  # enabled by default
    if debug != 0:
        debugger_host = os.environ.get('SISBAT_DEBUGGER_HOST', '192.168.3.100')
        import pydevd_pycharm

        print("setting up debugger server on {}:{}".format(debugger_host, 21000))
        pydevd_pycharm.settrace(debugger_host, port=21000, stdoutToServer=True, stderrToServer=True, suspend=False)

    logger.debug("Running Async client with asyncio loop not yet started")
    logger.debug("------------------------------------------------------")
    loop = asyncio.new_event_loop()
    assert not loop.is_running()
    asyncio.set_event_loop(loop)

    new_loop, client = ModbusClient(
        schedulers.ASYNC_IO,
        host=settings['modbustcp']['host'],
        port=settings['modbustcp']['port'],
        loop=loop
    )
    monitor = Monitor(client, settings, logger)
    loop.run_until_complete(monitor.run())
    loop.close()
    logger.debug("--------DONE RUN_WITH_NO_LOOP-------------")
    logger.debug("")