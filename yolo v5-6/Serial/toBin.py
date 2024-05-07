import serial
import serial.tools.list_ports

userSerial = 0

#查看串口设备
def dis_com():
    uart_list = list(serial.tools.list_ports.comports())
    if len(uart_list):
        print("uart:")
        for uart in uart_list:
            print(uart.name, uart.description)
    else:
        print("no uart.")

#打开指定设备
def open_com(com,bolv = 9600):
    com.replace(' ','')
    try:
        ser = serial.Serial(com, bolv, timeout=0.5)
        if ser.is_open:
            print(com + "打开成功")
            return ser
        else:
            print(com + "打开失败")
    except Exception as e:
        print("---打开串口异常---:", e)

#关闭指定设备
def close_com(serial):
    try:
        serial.close()
        print('串口已关闭')
    except Exception as e:
        print("---关闭串口异常---:", e)

#串口发bin文件 测试
def test_w(serial):
    with open('./pro.bin', 'rb') as f:
        a = f.read()
    print("正在发送bin文件")
    count = serial.write(a)
    print("发送完成，共发送字节数：", count)

def com_write(serial,str):
    if serial != 0:
        serial.write(str)
    else:
        print('串口没有打开')

print('--start')


while True:
    rdat =  input()

    if rdat == 'end':           #end            结束程序
        break
    elif rdat == 'dis com':     #dis com        查看当前串口设备
        dis_com()
    elif 'open COM' in rdat:    #open COMx      打开指定串口
        userSerial = open_com(rdat[5:])
    elif 'close COM' in rdat:   #close COMx      关闭 指定串口
        close_com(userSerial)
    elif 'w bin' in rdat:       #测试使用
        test_w(userSerial)
    elif 'com->:' in rdat:      #com->:         串口输出com->:之后的数据
        com_write(userSerial,rdat[6:])


print('--end')

# try:
#     ser = serial.Serial("COM10", 9600, timeout=0.5)
#     if ser.is_open:
#         print("COM10" + "打开成功")
#         with open('./pro.bin', 'rb') as f:
#             a = f.read()
#         print("正在发送bin文件")
#         count = ser.write(a)
#         print("发送完成，共发送字节数：", count)
 
# except Exception as e:
#     print("---异常---：", e)

