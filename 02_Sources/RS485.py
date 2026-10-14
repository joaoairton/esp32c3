import machine
import utime
from machine import Pin

def main():

    uart = machine.UART(1, baudrate=115200, tx=17, rx=18) 
    
    while True:
        
        if uart.any():
            # 读取串口数据
            data = uart.read()

            # 打印接收到的数据
            print("Received data:", data)
            
        # 暂停100毫秒
        utime.sleep_ms(100)
        uart.write('test')
        
if __name__ == '__main__':
    main()
