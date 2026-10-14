import machine
import utime
import time
import network
from machine import Pin
import usocket as socket
import sys
import ubinascii
import uos

GL_PWR = Pin(38, Pin.OUT)

def send_at(uart, cmd, timeout=2, wait_for_response=True):
    print(f"Send: {cmd}")
    uart.write(cmd + "\r\n")
    if not wait_for_response:
        return None
        
    start = utime.time()
    response = b""
    while (utime.time() - start) < timeout:
        if uart.any():
            response += uart.read()
            # 检查是否收到完整响应
            if b"OK" in response or b"ERROR" in response:
                break
        utime.sleep_ms(100)
    return response if response else None

def setup_modem():
    # 硬件初始化
    GL_PWR = Pin(38, Pin.OUT)
    GL_PWR.value(1)  # 使能供电
    uart = machine.UART(2, baudrate=115200, tx=39, rx=40)
    
    # 等待模块初始化
    print("Waiting for modem initialization...")
    utime.sleep(5)
    
    # 清空缓冲区
    while uart.any():
        uart.read()
    
    # AT指令序列
    responses = {}
    commands = [
        ('AT', "Basic test"),
        ('AT+CPIN?', "if is ready"),
        ('AT+CGDCONT=1,"IP","CMNET"', "Set APN"),
        ('AT+CGACT=1,1', "Activate PDP context"),
        ('AT+CGACT?', "检查状态"),
        ('AT+CGPADDR=1', "获取IP地址"),
    ]
    
    for cmd, desc in commands:
        print(f"Sending {desc}: {cmd}")
        resp = send_at(uart, cmd, 5)
        responses[cmd] = resp
        print("Response:", resp)
        utime.sleep(1)
    
    return uart

def do_tcp_test(uart):
    host = "112.125.89.8"
    port = "32370"
    cmd = 'AT+QIOPEN=1,0,"TCP","%s",%s,0,2' % (host, port) 
    resp = send_at(uart, cmd, 3)  # 增加超时时间，等待连接建立
    print("QIOPEN response:", resp)
    
    # 等待连接建立
    utime.sleep(2)
    
    count = 3
    while count > 0:
        if uart.any():
            # 读取串口数据
            data = uart.read()
            # 打印接收到的数据
            print("Received data:", data)
        
        # 发送消息并减少计数器
        uart.write('test')
        print("Sent: test")
        count -= 1
        
        utime.sleep(1)

    # 退出透传模式
    utime.sleep(1)  # 确保没有数据传输
    uart.write(b'+++')  # 发送退出序列，注意使用字节
    utime.sleep(1)  # 等待模块响应
    
    resp = send_at(uart, "AT+QICLOSE=0", 5)  # 断开连接
    


def main():
    try:
        uart = setup_modem()
        do_tcp_test(uart)
    except Exception as e:
        print("严重错误:", e)
        import traceback
        traceback.print_exc()
    finally:
        GL_PWR.value(0)

if __name__ == '__main__':
    main()