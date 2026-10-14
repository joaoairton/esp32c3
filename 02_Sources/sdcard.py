import machine
import os
import utime

def main():
    # 初始化SD卡
    sd = machine.SDCard(slot=2)

    # 挂载SD卡
    try:
        os.mount(sd, "/sd")
        print("SD card mounted.")
    except OSError as e:
        print("Error mounting SD card:", e)
    ret = os.listdir('/sd')
    print("SD card:", ret)
    #写入文件
    try:
        with open("/sd/test.txt", "w") as f:
            f.write("Hello, SD Card!")
        print("File written to SD card.")
        f.close()
    except OSError as e:
        print("Error writing to file:", e)
    ret = os.listdir('/sd')
    print("SD card:", ret)
    utime.sleep(1)
    # 读取文件
    try:
        with open("/sd/test.txt", "r") as f:
            content = f.read()
        print("File content:", content)
    except OSError as e:
        print("Error reading from file:", e)

    # 卸载SD卡
    try:
        os.umount("/sd")
        print("SD card unmounted.")
    except OSError as e:
        print("Error unmounting SD card:", e)

if __name__ == '__main__':
    main()
