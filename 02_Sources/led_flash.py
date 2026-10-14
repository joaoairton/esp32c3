import time
from machine import Pin

def main():
    # RTU一共2个可控指示灯
    led_wifi = Pin(45, Pin.OUT) # LED1 on GPIO 39 wifi
    led_sta = Pin(21, Pin.OUT) # LED2 on GPIO 21 运行
    while True:
        led_wifi.value(1)
        led_sta.value(1)
        print("led high")
        time.sleep(1)
        led_wifi.value(0) 
        led_sta.value(0)
        print("led low")
        time.sleep(1)

#程序启动入口
if __name__ == '__main__':
    main()
