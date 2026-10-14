import network
import machine
import time

def main():
    # 初始化SPI和引脚
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
    print(spi)
    # 激活接口
    lan.active(True)
    lan.config(mac=b'\xe4\xba\xba\xe7\x94\x9f')
    time.sleep(1)
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
        do_tcp_client() #tcp测试
def do_tcp_client():
    import socket
    import time

    # 服务器的IP地址和端口
    server_ip = '192.168.20.5'
    server_port = 8080  # 选择一个合适的端口号

    # 创建socket对象
    addr_info = socket.getaddrinfo(server_ip,server_port)
    addr = addr_info[0][-1]
    # 连接到服务器
    s = socket.socket()
    s.connect(addr)
    # 发送数据
    try:
        while True:
            print('send data')
            # 发送数据
            s.send(b'GET / HTTP/1.1\r\nHost: micropython.org\r\n\r\n')
            data = s.recv(1000)
            print(f"Received: {data.decode('utf-8')}")
            # 每隔1秒发送一次数据
            time.sleep(1)
            
            
    except KeyboardInterrupt:
        print("Client stopped by user.")
    finally:
        # 关闭连接
        client_socket.close()
        
 #程序启动入口
if __name__ == '__main__':
    main()       
