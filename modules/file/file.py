# quectel_file_demo.py - File模块完整演示

from quectel import File

print("=" * 50)
print("Quectel File Module Demo")
print("=" * 50)

# 1. 目录操作
print("\n1. 目录操作示例")
print("-" * 30)

# 创建目录
print("创建目录 test_dir...")
try:
    File.mkdir('test_dir')
    print("✅ 目录创建成功")
except Exception as e:
    print(f"❌ 目录创建失败: {e}")

# 列出根目录
print("\n列出根目录内容:")
for info in File.listdir('*'):
    if info.size() == -1:
        print(f"  📁 {info.name()}/ (目录)")
    else:
        print(f"  📄 {info.name()} ({info.size()} 字节)")

# 2. 文件写入操作
print("\n2. 文件写入示例")
print("-" * 30)

# 写入文本文件
print("写入文本文件 test.txt...")
with File.open("SD:test.txt", "w") as f:
    # 写入字符串（自动编码）
    f.write("Hello, Quectel!\n")
    f.write("这是第二行\n")
    f.write("你好，世界！\n")
print("✅ 文本写入完成")

# 写入二进制文件
print("\n写入二进制文件 binary.dat...")
with File.open("binary.dat", "w") as f:
    # 写入字节数据
    f.write(b'\x00\x01\x02\x03\x04\x05')
    f.write(b'ABCDE')
    f.write(bytes([0x48, 0x65, 0x6c, 0x6c, 0x6f]))  # "Hello"
print("✅ 二进制写入完成")

# 3. 文件读取操作
print("\n3. 文件读取示例")
print("-" * 30)

# 读取整个文件
print("读取 test.txt 全部内容:")
with File.open("test.txt", "r") as f:
    data = f.read(1024)
    print("-"  * 20)
    print(data.decode('utf-8'))
    print("-"  * 20)
    print(f"共读取 {len(data)} 字节")

# 逐字节读取
print("\n逐字节读取前10个字节:")
with File.open("test.txt", "r") as f:
    for i in range(10):
        b = f.read(1)
        print(f"  第{i}字节: {b} ({b.hex()})")

# 4. 文件指针操作
print("\n4. 文件指针操作示例")
print("-" * 30)

with File.open("test.txt", "r") as f:
    # 获取当前位置
    pos = f.tell()
    print(f"初始位置: {pos}")
    
    # 读取5个字节
    data = f.read(5)
    print(f"读取5字节后位置: {f.tell()}")
    
    # 移动到文件开头
    f.seek(0, File.SEEK_SET)
    print(f"SEEK_SET后位置: {f.tell()}")
    
    # 移动到文件末尾
    f.seek(0, File.SEEK_END)
    print(f"SEEK_END后位置: {f.tell()}")
    
    # 从末尾向前移动
    f.seek(10, File.SEEK_END)
    print(f"从末尾向前10字节后位置: {f.tell()}")
    last_10 = f.read(20)
    print(f"最后10字节: {last_10.decode('utf-8')}")

# 5. 文件信息
print("\n5. 文件信息示例")
print("-" * 30)

# 列出目录详细信息
print("test_dir 目录内容:")
for info in File.listdir('*'):
 #   if info.name().startswith('test') or info.name().startswith('binary'):
    print(f"  📄 {info.name()}: {info.size()} 字节")

# 6. 文件系统信息
print("\n6. 文件系统信息")
print("-" * 30)

total, free = File.statvfs("UFS")
print(f"总空间: {total} 字节 ({total/1024:.2f} KB, {total/1024/1024:.2f} MB)")
print(f"剩余空间: {free} 字节 ({free/1024:.2f} KB, {free/1024/1024:.2f} MB)")
print(f"已使用: {total - free} 字节 ({ (total-free)/total*100:.1f}%)")

# 7. 文件删除和目录删除
print("\n7. 文件删除示例")
print("-" * 30)

# 删除文件
print("删除 test.txt...")
try:
    File.remove("test.txt")
    print("✅ 文件删除成功")
except Exception as e:
    print(f"❌ 删除失败: {e}")

print("删除 binary.dat...")
try:
    File.remove("binary.dat")
    print("✅ 文件删除成功")
except Exception as e:
    print(f"❌ 删除失败: {e}")

# 8. 目录删除
print("\n8. 目录删除示例")
print("-" * 30)

# 先创建一个带文件的目录用于演示
print("创建测试目录 test_dir/subdir 和文件...")
File.mkdir('test_dir/subdir')
with File.open("test_dir/test.txt", "w") as f:
    f.write("这是一个测试文件")
print("目录和文件创建完成")

print("\n删除 test_dir 目录（非空，使用 force=True）...")
try:
    File.rmdir('test_dir', True)
    print("✅ 目录强制删除成功")
except Exception as e:
    print(f"❌ 删除失败: {e}")

# 9. 验证最终状态
print("\n9. 最终文件列表")
print("-" * 30)

count = 0
for info in File.listdir('*'):
    count += 1
    if info.size() == -1:
        print(f"  📁 {info.name()}/")
    else:
        print(f"  📄 {info.name()} ({info.size()} 字节)")

print("\n" + "=" * 50)
print("演示完成！")
print("=" * 50)