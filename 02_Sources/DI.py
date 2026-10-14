import time
import machine

def main():
    DI1 = machine.Pin(4, machine.Pin.IN,machine.Pin.PULL_DOWN)
    DI2 = machine.Pin(5, machine.Pin.IN,machine.Pin.PULL_DOWN)
    while True:
        di1_value = DI1.value()
        di2_value = DI2.value()
        print(f'[1]di1_value = {di1_value}, di2_value = {di2_value}')
        time.sleep(1)
        
if __name__ == '__main__':
    main()
