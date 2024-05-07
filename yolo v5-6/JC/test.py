# import time
#
# import serial
# import serial.tools.list_ports
# import threading
#
#
# userSerial = 0#串口对象
#
# ########################################################################### 通过串口连接底盘驱动板
# uart_list = list(serial.tools.list_ports.comports())
# if len(uart_list):
#     for uart in uart_list:
#         if 'CH340' in uart.description:
#             userSerial = serial.Serial(uart.name, 115200, timeout=0.5)
#     if userSerial == 0:
#         print('底盘驱动板连接失败')
#     else:
#         print('底盘驱动板连接成功')
# else:
#     print('底盘驱动板连接失败')
# ###########################################################################
#
#
# def serialReceiveThread(a):
#     global userSerial
#     while True:
#         if userSerial != 0:
#             serialRdata = userSerial.read(userSerial.inWaiting())
#             if len(serialRdata) != 0:
#                 serialRdata = serialRdata.decode('gbk')
#                 print('接收:' + serialRdata)
#
# #加上daemon = True后，主线程结束时，不会等待子线程结束
# #否则主线程会一直等子线程
# t1 = threading.Thread(target=serialReceiveThread,args=(1,),daemon=True)
# t1.start()
#
#
# #转向68，前进77
#
# userSerial.write('AA-77-77M'.encode('utf-8'))
#
# time.sleep(3)
#
# userSerial.write('AA+00+00M'.encode('utf-8'))
#
#
# while True:
#     pass


import requests

res =requests.get('http://192.168.4.1/js?json={%22T%22:1041,%22x%22:-350,%22y%22:-30,%22z%22:210,%22t%22:3.14}')