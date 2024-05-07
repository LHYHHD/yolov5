import serial
import serial.tools.list_ports
import threading
import os


userSerial = 0#串口对象

help_str = '''
#end            结束程序
#dis com        查看当前串口设备
#open COMx      打开指定串口
#com->:         串口输出com->:之后的数据
#help           查看帮助
'''



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
    global serialFlg
    com.replace(' ','')
    try:
        ser = serial.Serial(com, bolv, timeout=0.5)
        if ser.is_open:
            serialFlg = True
            print(com + "打开成功")
            return ser
        else:
            print(com + "打开失败")
    except Exception as e:
        print("---打开串口异常---:", e)

#关闭指定设备
def close_com(serial):
    global userSerial
    try:
        if serial != 0:
            serial.close()
        print('串口已关闭')
        userSerial = 0
    except Exception as e:
        print("---关闭串口异常---:", e)

#串口发bin文件 测试
def test_w(serial):
    with open('./pro.bin', 'rb') as f:
        a = f.read()
    print("正在发送bin文件")
    count = serial.write(a)
    print("发送完成，共发送字节数：", count)

#串口发送数据
def com_write(serial,str):
    if serial != 0:
        serial.write(str)
    else:
        print('串口没有打开')

def com_receive(serial):
    if serial != 0:
        serialRdata = serial.read(serial.inWaiting())
        if len(serialRdata) != 0:
            serialRdata = serialRdata.decode('gbk')
            print('接收:' + serialRdata)


print('--start')
print('--输入\'help\'查看帮助')
#串口接收数据线程
def serialReceiveThread(a): 
    global userSerial
    while True:
        if userSerial != 0:
            serialRdata = userSerial.read(userSerial.inWaiting())
            if len(serialRdata) != 0:
                serialRdata = serialRdata.decode('gbk')
                print('接收:' + serialRdata)

#加上daemon = True后，主线程结束时，不会等待子线程结束
#否则主线程会一直等子线程
t1 = threading.Thread(target=serialReceiveThread,args=(1,),daemon=True)
t1.start()



while True:
    rdat =  input()

    if rdat == 'end':           #end            结束程序
        break
    elif rdat == 'dis com':     #dis com        查看当前串口设备
        dis_com()
    elif 'open COM' in rdat:    #open COMx      打开指定串口
        userSerial = open_com(rdat[5:],115200)
    elif 'close COM' in rdat:   #close COMx      关闭 指定串口
        close_com(userSerial)
    elif 'w bin' in rdat:       #测试使用
        test_w(userSerial)
    elif 'com->:' in rdat:      #com->:         串口输出com->:之后的数据
        com_write(userSerial,rdat[6:])
    elif 'help' in rdat:
        print(help_str)         #help:         输出指令作用   

print('--end')
close_com(userSerial)



