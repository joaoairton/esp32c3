#tcp服务端收发数据测试
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
        
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('CMCC-AbPL', 'EC12345678')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    print(wlan.isconnected())
    do_tcp_client()

#程序启动入口
if __name__ == '__main__':
    do_connect()
    


