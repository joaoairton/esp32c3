import machine
import os
import utime
import uos

# 初始化SD卡
sd = machine.SDCard(slot=2)

# 挂载SD卡
try:
    os.mount(sd, "/sd")
    print("SD card mounted.")
except OSError as e:
    print("Error mounting SD card:", e)
    # 如果挂载失败，退出程序
    raise

# 显示SD卡上的文件
ret = os.listdir('/sd')
print("SD card contents:", ret)

# 测试参数
file_size = 100 * 1024  # 100KB测试文件
test_file = "/sd/speed_test.bin"
chunk_size = 4096  # 每次写入/读取的数据块大小

# 生成测试数据
test_data = bytearray(b'A' * chunk_size)

# 写入速度测试
print("\n=== 写入速度测试 ===")
print(f"测试文件: {test_file}")
print(f"文件大小: {file_size/1024} KB")

# 删除可能已存在的测试文件
try:
    os.remove(test_file)
except OSError:
    pass

# 开始写入测试
start_time = utime.ticks_ms()
bytes_written = 0

try:
    with open(test_file, "wb") as f:
        while bytes_written < file_size:
            chunk = min(chunk_size, file_size - bytes_written)
            f.write(test_data[:chunk])
            bytes_written += chunk
    write_time = utime.ticks_diff(utime.ticks_ms(), start_time)
    
    # 计算写入速度
    write_speed = (bytes_written / 1024) / (write_time / 1000)  # KB/s
    print(f"写入时间: {write_time/1000:.2f} 秒")
    print(f"写入速度: {write_speed:.2f} KB/s")
    
except OSError as e:
    print("写入测试失败:", e)

# 读取速度测试
print("\n=== 读取速度测试 ===")

# 确保文件存在
if test_file in os.listdir('/sd'):
    start_time = utime.ticks_ms()
    bytes_read = 0
    
    try:
        with open(test_file, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                bytes_read += len(chunk)
        read_time = utime.ticks_diff(utime.ticks_ms(), start_time)
        
        # 计算读取速度
        read_speed = (bytes_read / 1024) / (read_time / 1000)  # KB/s
        print(f"读取时间: {read_time/1000:.2f} 秒")
        print(f"读取速度: {read_speed:.2f} KB/s")
        
    except OSError as e:
        print("读取测试失败:", e)
else:
    print("测试文件不存在，无法进行读取测试")

# 清理测试文件
try:
    os.remove(test_file)
    print(f"\n已清理测试文件: {test_file}")
except OSError:
    pass

# 显示SD卡剩余空间
fs_stat = uos.statvfs('/sd')
total_blocks = fs_stat[0] * fs_stat[2]
free_blocks = fs_stat[0] * fs_stat[3]
total_kb = total_blocks / 1024
free_kb = free_blocks / 1024
used_kb = total_kb - free_kb

print(f"\n=== SD卡空间信息 ===")
print(f"总空间: {total_kb:.2f} KB")
print(f"已用空间: {used_kb:.2f} KB")
print(f"可用空间: {free_kb:.2f} KB")

# 卸载SD卡
try:
    os.umount("/sd")
    print("\nSD card unmounted.")
except OSError as e:
    print("Error unmounting SD card:", e)