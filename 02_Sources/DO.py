import time
import machine

def main():
    # RTU一共2个DO
    DO1 = machine.Pin(15, machine.Pin.OUT)  
    DO2 = machine.Pin(16, machine.Pin.OUT)  
    while True:
        DO1.value(1)
        time.sleep(0.5)
        DO2.value(1)
        print("DO output high")
        time.sleep(1)
        DO1.value(0)
        time.sleep(0.5)
        DO2.value(0)
        print("DO output low")
        time.sleep(1)

#程序启动入口
if __name__ == '__main__':
    main()
