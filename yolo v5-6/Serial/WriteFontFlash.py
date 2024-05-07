import serial
import serial.tools.list_ports
import threading
import os
import time


#同时接收字库数据的设备个数
device  = 1
#英文字库目录
charPath = "C:\\Users\\LHYHHYD_\\Desktop\\文件系统\\汉字显示\\CHAR_FONT_16.FON"
#汉字字库目录
fontPath = "C:\\Users\\LHYHHYD_\\Desktop\\文件系统\\汉字显示\\GB2312\\GB2312_16_ST.FON"


#获取英文字模大小
charSize = os.path.getsize(charPath)
#获取汉字字模大小
fontSize = os.path.getsize(fontPath)
allSizeStr = str(charSize+fontSize)


userSerial = 0#串口对象

help_str = '''
end            结束程序
dis com        查看当前串口设备
open COMx      打开指定串口
com->:         串口输出com->:之后的数据
help           查看帮助
write font     写入字库数据
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

ifOK = 0

#串口接收数据线程
def serialReceiveThread(a): 
    global userSerial,ifOK
    while True:
        if userSerial != 0:
            serialRdata = userSerial.read(userSerial.inWaiting())
            if len(serialRdata) != 0:
                serialRdata = serialRdata.decode('gbk')
                print('接收:' + serialRdata)
                if 'K' in serialRdata:
                    serialRdata = ' '
                    ifOK += 1

#加上daemon = True后，主线程结束时，不会等待子线程结束
#否则主线程会一直等子线程
t1 = threading.Thread(target=serialReceiveThread,args=(1,),daemon=True)
t1.start()


#将程序写入flash,需要单片机程序配套使用,写完方可退出
#deviceNum：同时接收字库数据的设备个数
def autoWriteFont(deviceNum ,char_path,font_path):
    global userSerial,ifOK,charSize,fontSize
    tim = time.time()
    w_cont = 0
    if userSerial == 0:
        print('串口未打开')
    else:
        print('开始传输字模')
        path = char_path
        r_add = 0
        while True:                     #开始传输英文字模，直至英文字模传输完成
            with open(path,'rb') as f:  #'rb'按字节读取数据，'r'按字符读取数据
                f.seek(r_add)           #设置光标位置
                dat = f.read(250)       #读取250字节(如果文件不足250字节，会自动读出有限数据)
                r_add += 250            #地址偏移250，不用考虑位置超标，因为下面有判断
                cont = userSerial.write(dat)#通过串口发送数据，返回的是实际发送的字节数
                w_cont += cont          #发送的总字节数
                print(f'{w_cont}/'+allSizeStr)#进度显示
                while ifOK != deviceNum:#发送完后等待接收设备响应
                    pass
                ifOK = 0                #清除接收设备响应标志位
            if w_cont == charSize:      #英文字模发送完成
                break
        path = font_path                #开始发送中文字模
        r_add = 0                       #读取光标位置置0
        print('英文字符更新完毕')
        userSerial.write('1OK'.encode('gbk'))#高速接收设备开始英文字模传输完成
        while ifOK != deviceNum:        #等待设备响应
            pass
        ifOK = 0                        #清除接收设备响应标志位
        while True:                     #开始传输汉字字模，直至汉字字模传输完成
            with open(path,'rb') as f:  #'rb'按字节读取数据，'r'按字符读取数据
                f.seek(r_add)           #设置光标位置
                dat = f.read(250)       #读取250字节(如果文件不足250字节，会自动读出有限数据)
                r_add += 250            #地址偏移250，不用考虑位置超标，因为下面有判断
                cont = userSerial.write(dat)#通过串口发送数据，返回的是实际发送的字节数
                w_cont += cont          #发送的总字节数,要注意的是，发送完英文字模后，这个变量是没有清零的
                print(f'{w_cont}/'+allSizeStr)#进度显示
                while ifOK != deviceNum:#发送完后等待接收设备响应
                    pass
                ifOK = 0                #清除接收设备响应标志位
            if w_cont == charSize+fontSize:#所有字模发送完成
                break
        userSerial.write('2OK'.encode('gbk'))#通知从设备所有字模发送完成
        print('总耗时:',time.time() - tim,'秒')
                

print('--start')
print('--输入\'help\'查看帮助')

while True:
    rdat =  input()

    if rdat == 'end':           #end                结束程序
        break
    elif rdat == 'dis com':     #dis com            查看当前串口设备
        dis_com()
    elif 'open COM' in rdat:    #open COMx          打开指定串口
        userSerial = open_com(rdat[5:],115200)
    elif 'close COM' in rdat:   #close COMx         关闭 指定串口
        close_com(userSerial)
    elif 'w bin' in rdat:       #测试使用
        test_w(userSerial)
    elif 'com->:' in rdat:      #com->:             串口输出com->:之后的数据
        com_write(userSerial,rdat[6:])
    elif 'write font' in rdat:  #write font         开始发送字库数据
        autoWriteFont(device,charPath,fontPath)
    elif 'help' in rdat:
        print(help_str)         #help:              输出指令作用   

print('--end')
if userSerial != 0:
    close_com(userSerial)



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

