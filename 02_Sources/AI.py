# ai测试案例
# ai1-gpio1,ai2-gpio11 电流测量范围4-20ma
from machine import ADC
import time
import machine

def main():
    ai1 = ADC(machine.Pin(6)) #ai1
    ai1.atten(ADC.ATTN_11DB)  #使用0衰减，精度最高，输入电压范围：0-950mv
    ai2 = ADC(machine.Pin(7)) #ai2
    ai2.atten(ADC.ATTN_11DB)
    while True:
        val_u16_1 = ai1.read_u16()  # read a raw analog value in the range 0-65535
        val_uv_1 = ai1.read_uv()   # read an analog value in microvolts
        val_raw1 = ai1.read() #获取原始ADC值
        print(f'val_u16_1 = {val_u16_1}, val_uv_1 = {val_uv_1}',f'val_raw1 = {val_raw1}',f'ai1 = {val_uv_1/150/1000}ma')
        time.sleep(0.5)
        val_u16_2 = ai2.read_u16()  # read a raw analog value in the range 0-65535
        val_uv_2 = ai2.read_uv()   # read an analog value in microvolts
        value2 = ai2.read() #获取原始ADC值
        print(f'val_u16_2 = {val_u16_2}, val_uv_2 = {val_uv_2}',f'val_raw2 = {val_raw2}',f'ai2 = {val_uv_2/150/1000}ma')
        time.sleep(0.5)
        
if __name__ == '__main__':
    main()