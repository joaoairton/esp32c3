import uModBusConst as Const
import struct
import socket
import network
import utime as time
from machine import Pin
import machine

# ========== 网络配置 ==========
NETWORK_CONFIG = {
    'ip': '192.168.20.76',        # 设备IP地址
    'subnet': '255.255.255.0',    # 子网掩码
    'gateway': '',                # 网关（可选）
    'dns': '8.8.8.8'             # DNS服务器
}

# ========== Modbus从站配置 ==========
MODBUS_CONFIG = {
    'port': 502,                  # Modbus TCP端口
    'slave_id': 1,                # 从站ID
    'coils_size': 1000,           # 线圈数量
    'registers_size': 1000        # 寄存器数量
}

# ========== W5500硬件配置 ==========
W5500_CONFIG = {
    'spi_id': 1,
    'baudrate': 20_000_000,       # SPI时钟频率
    'sck_pin': 12,
    'mosi_pin': 11,
    'miso_pin': 13,
    'cs_pin': 47,
    'reset_pin': 48,
    'int_pin': 14,
    'phy_addr': 0,
    'ref_clk_mode': 1,
    'ref_clk': 25
}

class uModBusTCPSlave:
    def __init__(self, port=MODBUS_CONFIG['port'], slave_id=MODBUS_CONFIG['slave_id']):
        self.port = port
        self.slave_id = slave_id
        # 使用配置中的大小初始化数据存储
        self.coils = [False] * MODBUS_CONFIG['coils_size']
        self.discrete_inputs = [False] * MODBUS_CONFIG['coils_size']
        self.holding_registers = [0] * MODBUS_CONFIG['registers_size']
        self.input_registers = [0] * MODBUS_CONFIG['registers_size']
        self._sock = None
        self._running = False
        
    def start(self):
        """启动Modbus TCP从站服务器"""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind(('0.0.0.0', self.port))
            self._sock.listen(5)
            self._running = True
            print(f"Modbus TCP Slave started on port {self.port}, Slave ID: {self.slave_id}")
            print(f"Data sizes - Coils: {len(self.coils)}, Registers: {len(self.holding_registers)}")
            
            while self._running:
                try:
                    conn, addr = self._sock.accept()
                    print(f"Connection from {addr}")
                    self._handle_client(conn)
                except Exception as e:
                    print(f"Connection error: {e}")
        except Exception as e:
            print(f"Failed to start Modbus server: {e}")
    
    def _handle_client(self, conn):
        """处理客户端请求"""
        try:
            while True:
                # 接收MBAP头
                mbap_header = conn.recv(7)
                if len(mbap_header) < 7:
                    break
                    
                # 解析MBAP头
                trans_id, proto_id, length, unit_id = struct.unpack('>HHHB', mbap_header)
                
                # 接收PDU
                pdu = conn.recv(length - 1)  # 减去unit_id的1字节
                
                if not pdu:
                    break
                    
                # 处理请求并生成响应
                response = self._process_request(pdu, unit_id)
                if response:
                    # 构建响应MBAP头
                    resp_mbap = struct.pack('>HHHB', trans_id, proto_id, len(response) + 1, unit_id)
                    conn.send(resp_mbap + response)
                    
        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            conn.close()
            print("Client disconnected")
    
    def _process_request(self, pdu, unit_id):
        """处理Modbus请求PDU并生成响应"""
        if unit_id != self.slave_id and unit_id != 0:
            return self._build_exception_response(pdu[0], Const.ILLEGAL_DATA_ADDRESS)
            
        function_code = pdu[0]
        
        try:
            if function_code == Const.READ_COILS:
                return self._read_coils(pdu)
            elif function_code == Const.READ_DISCRETE_INPUTS:
                return self._read_discrete_inputs(pdu)
            elif function_code == Const.READ_HOLDING_REGISTERS:
                return self._read_holding_registers(pdu)
            elif function_code == Const.READ_INPUT_REGISTER:
                return self._read_input_registers(pdu)
            elif function_code == Const.WRITE_SINGLE_COIL:
                return self._write_single_coil(pdu)
            elif function_code == Const.WRITE_SINGLE_REGISTER:
                return self._write_single_register(pdu)
            elif function_code == Const.WRITE_MULTIPLE_COILS:
                return self._write_multiple_coils(pdu)
            elif function_code == Const.WRITE_MULTIPLE_REGISTERS:
                return self._write_multiple_registers(pdu)
            else:
                return self._build_exception_response(function_code, Const.ILLEGAL_FUNCTION)
                
        except Exception as e:
            print(f"Process request error: {e}")
            return self._build_exception_response(function_code, Const.ILLEGAL_DATA_VALUE)
    
    def _read_coils(self, pdu):
        """处理读取线圈请求 (0x01)"""
        start_addr, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 2000):
            return self._build_exception_response(Const.READ_COILS, Const.ILLEGAL_DATA_VALUE)
        
        if start_addr + quantity > len(self.coils):
            return self._build_exception_response(Const.READ_COILS, Const.ILLEGAL_DATA_ADDRESS)
            
        # 生成响应数据
        byte_count = (quantity + 7) // 8
        response_data = bytearray(byte_count + 2)  # 功能码 + 字节数 + 数据
        response_data[0] = Const.READ_COILS
        response_data[1] = byte_count
        
        for i in range(quantity):
            if self.coils[start_addr + i]:
                response_data[2 + i // 8] |= (1 << (i % 8))
                
        return bytes(response_data)
    
    def _read_holding_registers(self, pdu):
        """处理读取保持寄存器请求 (0x03)"""
        start_addr, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 125):
            return self._build_exception_response(Const.READ_HOLDING_REGISTERS, Const.ILLEGAL_DATA_VALUE)
        
        if start_addr + quantity > len(self.holding_registers):
            return self._build_exception_response(Const.READ_HOLDING_REGISTERS, Const.ILLEGAL_DATA_ADDRESS)
            
        # 生成响应数据
        byte_count = quantity * 2
        response_data = bytearray(byte_count + 2)  # 功能码 + 字节数 + 数据
        response_data[0] = Const.READ_HOLDING_REGISTERS
        response_data[1] = byte_count
        
        for i in range(quantity):
            reg_value = self.holding_registers[start_addr + i]
            response_data[2 + i * 2] = (reg_value >> 8) & 0xFF
            response_data[3 + i * 2] = reg_value & 0xFF
                
        return bytes(response_data)
    
    def _write_single_register(self, pdu):
        """处理写单个寄存器请求 (0x06)"""
        addr, value = struct.unpack('>HH', pdu[1:5])
        
        if addr < len(self.holding_registers):
            self.holding_registers[addr] = value
            print(f"Register {addr} set to {value}")
            # 返回相同的请求作为响应
            return pdu
            
        return self._build_exception_response(Const.WRITE_SINGLE_REGISTER, Const.ILLEGAL_DATA_ADDRESS)
    
    def _write_multiple_registers(self, pdu):
        """处理写多个寄存器请求 (0x10)"""
        start_addr, quantity, byte_count = struct.unpack('>HHB', pdu[1:6])
        
        if not (1 <= quantity <= 123) or byte_count != quantity * 2:
            return self._build_exception_response(Const.WRITE_MULTIPLE_REGISTERS, Const.ILLEGAL_DATA_VALUE)
        
        if start_addr + quantity > len(self.holding_registers):
            return self._build_exception_response(Const.WRITE_MULTIPLE_REGISTERS, Const.ILLEGAL_DATA_ADDRESS)
            
        # 写入寄存器值
        for i in range(quantity):
            reg_value = struct.unpack('>H', pdu[6 + i * 2:8 + i * 2])[0]
            self.holding_registers[start_addr + i] = reg_value
        
        print(f"Registers {start_addr} to {start_addr + quantity - 1} updated")
        # 返回确认响应
        return struct.pack('>BHH', Const.WRITE_MULTIPLE_REGISTERS, start_addr, quantity)
    
    def _build_exception_response(self, function_code, exception_code):
        """构建异常响应"""
        return struct.pack('>BB', function_code + Const.ERROR_BIAS, exception_code)
    
    # 其他功能码的处理方法（待实现）
    def _read_discrete_inputs(self, pdu):
        """处理读取离散输入请求 (0x02)"""
        # 实现与_read_coils类似
        start_addr, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 2000):
            return self._build_exception_response(Const.READ_DISCRETE_INPUTS, Const.ILLEGAL_DATA_VALUE)
        
        if start_addr + quantity > len(self.discrete_inputs):
            return self._build_exception_response(Const.READ_DISCRETE_INPUTS, Const.ILLEGAL_DATA_ADDRESS)
            
        byte_count = (quantity + 7) // 8
        response_data = bytearray(byte_count + 2)
        response_data[0] = Const.READ_DISCRETE_INPUTS
        response_data[1] = byte_count
        
        for i in range(quantity):
            if self.discrete_inputs[start_addr + i]:
                response_data[2 + i // 8] |= (1 << (i % 8))
                
        return bytes(response_data)
        
    def _read_input_registers(self, pdu):
        """处理读取输入寄存器请求 (0x04)"""
        # 实现与_read_holding_registers类似
        start_addr, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 125):
            return self._build_exception_response(Const.READ_INPUT_REGISTER, Const.ILLEGAL_DATA_VALUE)
        
        if start_addr + quantity > len(self.input_registers):
            return self._build_exception_response(Const.READ_INPUT_REGISTER, Const.ILLEGAL_DATA_ADDRESS)
            
        byte_count = quantity * 2
        response_data = bytearray(byte_count + 2)
        response_data[0] = Const.READ_INPUT_REGISTER
        response_data[1] = byte_count
        
        for i in range(quantity):
            reg_value = self.input_registers[start_addr + i]
            response_data[2 + i * 2] = (reg_value >> 8) & 0xFF
            response_data[3 + i * 2] = reg_value & 0xFF
                
        return bytes(response_data)
        
    def _write_single_coil(self, pdu):
        """处理写单个线圈请求 (0x05)"""
        addr, value = struct.unpack('>HH', pdu[1:5])
        
        # 验证线圈值
        if value not in [0x0000, 0xFF00]:
            return self._build_exception_response(Const.WRITE_SINGLE_COIL, Const.ILLEGAL_DATA_VALUE)
            
        if addr < len(self.coils):
            self.coils[addr] = (value == 0xFF00)
            print(f"Coil {addr} set to {self.coils[addr]}")
            return pdu
            
        return self._build_exception_response(Const.WRITE_SINGLE_COIL, Const.ILLEGAL_DATA_ADDRESS)
        
    def _write_multiple_coils(self, pdu):
        """处理写多个线圈请求 (0x0F)"""
        start_addr, quantity, byte_count = struct.unpack('>HHB', pdu[1:6])
        
        expected_byte_count = (quantity + 7) // 8
        if not (1 <= quantity <= 1968) or byte_count != expected_byte_count:
            return self._build_exception_response(Const.WRITE_MULTIPLE_COILS, Const.ILLEGAL_DATA_VALUE)
        
        if start_addr + quantity > len(self.coils):
            return self._build_exception_response(Const.WRITE_MULTIPLE_COILS, Const.ILLEGAL_DATA_ADDRESS)
            
        # 写入线圈值
        for i in range(quantity):
            byte_index = 6 + (i // 8)
            bit_index = i % 8
            byte_val = pdu[byte_index]
            self.coils[start_addr + i] = bool(byte_val & (1 << bit_index))
        
        print(f"Coils {start_addr} to {start_addr + quantity - 1} updated")
        return struct.pack('>BHH', Const.WRITE_MULTIPLE_COILS, start_addr, quantity)
    
    def set_holding_register(self, address, value):
        """设置保持寄存器值（用于内部更新数据）"""
        if address < len(self.holding_registers):
            self.holding_registers[address] = value
            return True
        return False
    
    def set_coil(self, address, value):
        """设置线圈值（用于内部更新数据）"""
        if address < len(self.coils):
            self.coils[address] = bool(value)
            return True
        return False
    
    def stop(self):
        """停止服务器"""
        self._running = False
        if self._sock:
            self._sock.close()
        print("Modbus TCP Slave stopped")

class ModbusDataUpdater:
    def __init__(self, slave):
        self.slave = slave
        self.counter = 0
        self.timer = None
        
    def start_updating(self):
        """启动数据更新定时器"""
        self.timer = machine.Timer(0)
        self.timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self._update_callback)
        print("数据更新定时器已启动")
        
    def _update_callback(self, timer):
        """定时器回调函数"""
        self.counter += 1
        
        # 更新寄存器值
        self.slave.set_holding_register(0, 1000 + self.counter)
        self.slave.set_holding_register(1, 2000 + self.counter * 2)
        
        # 更新线圈状态（交替变化）
        self.slave.set_coil(0, self.counter % 2 == 0)
        self.slave.set_coil(1, self.counter % 3 == 0)
        
        # 可选：打印调试信息
        if self.counter % 10 == 0:
            print(f"数据已更新 {self.counter} 次")
            
    def stop_updating(self):
        """停止数据更新"""
        if self.timer:
            self.timer.deinit()
            self.timer = None
        print("数据更新定时器已停止")

def connect_w5500():
    """连接W5500以太网模块"""
    spi = machine.SPI(
        W5500_CONFIG['spi_id'], 
        baudrate=W5500_CONFIG['baudrate'],
        sck=machine.Pin(W5500_CONFIG['sck_pin']),
        mosi=machine.Pin(W5500_CONFIG['mosi_pin']),
        miso=machine.Pin(W5500_CONFIG['miso_pin'])
    )
    cs_pin = machine.Pin(W5500_CONFIG['cs_pin'], machine.Pin.OUT)
    reset_pin = machine.Pin(W5500_CONFIG['reset_pin'], machine.Pin.OUT)
    int_pin = machine.Pin(W5500_CONFIG['int_pin'], machine.Pin.IN)
    
    # 创建LAN接口
    lan = network.LAN(
        phy_type=network.PHY_W5500,
        reset=reset_pin,
        spi=spi,
        cs=cs_pin,
        int=int_pin,
        phy_addr=W5500_CONFIG['phy_addr'],
        ref_clk_mode=W5500_CONFIG['ref_clk_mode'],
        ref_clk=W5500_CONFIG['ref_clk']
    )

    # 配置网络
    lan.ifconfig((NETWORK_CONFIG['ip'], NETWORK_CONFIG['subnet'], 
                  NETWORK_CONFIG['gateway'], NETWORK_CONFIG['dns']))
    lan.active(True)
    
    # 等待连接（最多等待10秒）
    start_time = time.time()
    while not lan.isconnected():
        if time.time() - start_time > 10:
            print("连接超时！")
            return False
        time.sleep_ms(500)
        print("等待网络连接...")

    # 打印网络配置
    if lan.isconnected():
        print("网络连接成功！")
        print(f"IP地址: {lan.ifconfig()[0]}")
        mac_addr = ":".join("{:02x}".format(b) for b in lan.config("mac"))
        print(f"MAC地址: {mac_addr}")
        return True
    return False

# 使用示例
if __name__ == '__main__':
    print("=== Modbus TCP Slave 启动 ===")
    print(f"目标IP: {NETWORK_CONFIG['ip']}")
    print(f"Modbus端口: {MODBUS_CONFIG['port']}")
    print(f"从站ID: {MODBUS_CONFIG['slave_id']}")
    
    # 连接网络
    if connect_w5500():
        slave = uModBusTCPSlave(
            port=MODBUS_CONFIG['port'], 
            slave_id=MODBUS_CONFIG['slave_id']
        )
        
        # 初始化示例数据
        slave.set_holding_register(0, 1234)
        slave.set_holding_register(1, 5678)
        
        # 创建数据更新器
        updater = ModbusDataUpdater(slave)
        updater.start_updating()
        
        print("Modbus服务器开始运行...")
        
        # 启动服务器
        try:
            slave.start()
        except KeyboardInterrupt:
            print("程序被用户中断")
        finally:
            updater.stop_updating()
            slave.stop()
    else:
        print("网络连接失败，无法启动Modbus服务器")