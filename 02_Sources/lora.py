import machine
import utime
from machine import Pin

def main():
    M1 = Pin(41, Pin.OUT)  
    M1.value(0)
    utime.sleep_ms(1000)
    uart = machine.UART(2, baudrate=9600, tx=39, rx=40) 
    #uart.write('hello')
    #uart.write('AT+UART=?')
    
    while True:
        
        if uart.any():
            # 读取串口数据
            data = uart.read()

            # 打印接收到的数据
            print("Received data:", data)
            
        # 暂停1000毫秒
        utime.sleep_ms(1000)
        uart.write('test')
        
if __name__ == '__main__':
    main()
