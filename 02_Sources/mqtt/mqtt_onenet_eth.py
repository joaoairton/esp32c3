import ujson
import _thread
import network
from umqtt.simple import MQTTClient
import time
import machine
import ubinascii


Broker_Address="mqtts.heclouds.com"
password="version=2018-10-31&res=products%2Fgl6UsDOW54%0A%2Fdevice**********"
User_Name="gl6UsDOW54"
client_ID ="switch"
Broker_Port=1883
# 服务质量
qos = 0
# topic
get_topic = "$sys/gl6UsDOW54/switch/thing/property/post/reply" 
post_topic = "$sys/gl6UsDOW54/switch/thing/property/post"  # 上报属性

# 固定设备ID
device_id = "2478075109"

BrightValue = 75

connect_status_4g = False

def connect_eth():
    # 初始化SPI和引脚
    spi = machine.SPI(1, 
                    baudrate=5_000_000,  # 20MHz时钟
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


# 定义subcribe的回调函数
def on_subcribe(topic,msg):
    data = ((topic, msg))
    # print(data)
    payload = data[1]
    print(payload,type(payload))
    try:
        cloudmsg = ujson.loads(payload)
    except Exception :
         print("this is not json type!!!")
    else:
        if isinstance(cloudmsg,dict):      #检查收到的数据是否是标准的json格式
            if "key" in cloudmsg:          #平台设置
                print('key')

#mqtt数据接收监测
def mqttloop_func(delay, id):
    global client
    n= 0
    while True:
        time.sleep_ms(delay)
        try:
            n+=1
            client.check_msg()
            # print(n)
            if n>=10:
                client.ping()
                n = 0
                print('ping')
        except:
            print("mqtt disconnect!")
            client.disconnect()
            mqtt_reconnect()

#mqtt重新连接
def mqtt_reconnect():
    global client,Broker_Address, password, User_Name,Broker_Port,client_ID
    client = MQTTClient(client_ID, Broker_Address,Broker_Port,User_Name,password,60) 
    client.set_callback(on_subcribe)
    print("-------------1")
    client.connect() 
    print("-------------2")
    client.subscribe(get_topic)
    update()  # 连接成功后发送一次数据

#mqtt首次连接
def mqtt_connect():
    mqtt_reconnect()
    _thread.start_new_thread(mqttloop_func,(1500, 1))  #创建mqtt接收数据任务，1.5s一次

#上传数据到OneNET平台
def update(params=None):
    global client, device_id
    
    # 如果没有提供参数，使用默认值
    if params is None:
        params = {
            "BrightValue": {
                "value": 50
            }
        }
    
    # 构建符合OneNET平台要求的数据格式
    send_data = {
        "id": device_id,
        "version": "1.0",
        "params": params
    }
    
    MSG = ujson.dumps(send_data)
    print("发送数据:", MSG)
    client.publish(topic=post_topic, msg=MSG, retain=False, qos=0)

# 发送特定属性的便捷函数
def update_property(property_name, property_value):
    params = {
        property_name: {
            "value": property_value
        }
    }
    update(params)

if __name__ == '__main__':
    connect_eth()
    mqtt_connect()
    number = 0
    while True:
        number += 1
        time.sleep(1)
        if number >= 30:
            # 使用默认值发送数据
            #update()
            # 或者使用特定属性值
            update_property("BrightValue", BrightValue)
            BrightValue = (BrightValue + 1) % 255
            number = 0