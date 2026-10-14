# -*- encoding: utf-8 -*-import uModBusTCP as mt
import uModBusTCPPoll as mt
import utime as time
import network
import socket
import machine

# 电脑网口ip
SERVER = "192.168.20.5"
PORT = 8080

def connect_w5500():
    spi = machine.SPI(1, 
                baudrate=20_000_000,  # 20MHz时钟
                sck=machine.Pin(12),
                mosi=machine.Pin(11),
                miso=machine.Pin(13))
    cs_pin = machine.Pin(47, machine.Pin.OUT)  # 片选引脚
    reset_pin = machine.Pin(48, machine.Pin.OUT)
    int_pin = machine.Pin(14, machine.Pin.IN)  # 中断引脚（可选）
    
    # 创建LAN接口
    lan = network.LAN(
        phy_type=network.PHY_W5500,  # 指定W5500驱动
        reset=reset_pin,
        spi=spi,                     # SPI总线对象
        cs=cs_pin,                   # 片选引脚
        int=int_pin,                 # 中断引脚（可省略）
        phy_addr=0,                  # PHY地址（SPI模式下通常为0）
        ref_clk_mode=1,              # 参考时钟模式（0=输入，1=输出）
        ref_clk=25                   # 参考时钟引脚（根据硬件设计）
    )

    lan.active(True)

    # 等待连接（最多等待10秒）
    start_time = time.time()
    while not lan.isconnected():
        if time.time() - start_time > 10:
            print("连接超时！")
            break
        time.sleep_ms(500)
        print("等待连接...")

    # 打印网络配置
    if lan.isconnected():
        print("连接成功！")
        print("IP地址:", lan.ifconfig()[0])
        print("MAC地址:", ":".join("{:02x}".format(b) for b in lan.config("mac")))

def test_connectivity(host, port):
    try:
        addr_info = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.settimeout(5)
        s.connect(addr_info)
        s.close()
        return True
    except Exception as e:
        print(f"连通性测试失败: {e}")
        return False


def connect_modbus(retries=5, delay=2):
    for i in range(retries):
        try:
            print(f"尝试连接到Modbus服务器 ({i+1}/{retries})...")
            master = mt.uModBusTCP(SERVER, PORT, timeout=5)
            print("成功连接到Modbus服务器")
            return master
        except OSError as e:
            print(f"连接失败: {e}")
            if i < retries - 1:
                print(f"{delay}秒后重试...")
                time.sleep(delay)
            else:
                print("达到最大重试次数，无法连接到Modbus服务器。")
                raise

if __name__ == '__main__':
    print("开始初始化...")
    connect_w5500()
    # 在主程序中使用
    if test_connectivity(SERVER, PORT):
        print("网络连通性正常")
    else:
        print("无法连接到服务器，请检查网络设置")
    try:
        
        master = connect_modbus()
        
        while True:

            value = master.read_holding_registers(1, 0, 5)
            print("读取的值:", value)
            time.sleep(1)

    except Exception as e:
        print(f"Modbus连接失败: {e}")