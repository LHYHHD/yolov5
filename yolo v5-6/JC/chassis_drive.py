import serial
import serial.tools.list_ports
import time
import RoArm_drive
import chassis_drive

zx_speed = 75#底盘转向速度
qj_speed1 = 79#底盘前进速度1
qj_speed2 = 68#底盘前进速度2

userSerial = 0#串口对象

# 底盘电机控制：
# 	A A 正负 转速L 转速L 正负 转速R 转速R M
# 	实际转速为 转速L * 10
# 	占空比范围 0~1000
# 	例："AA+79+79M" 表示车子以790占空比前进
#
# 爪子角度控制：
# 	A B 正负 等级 保留 保留 保留 保留 M
# 	正负为 + 表示爪子闭合 ，为 - 表示爪子张开
# 	等级表示爪子张开或者闭合程度0为极限，依此后推
# 	例：	"AB+0MMMMM" 表示爪子完全闭合
# 			"AB-1MMMMM" 表示爪子完全张开

def control_dp(x,y,d):
    try:
        #转向优先级大于前进优先级
        # if x < 60 or x > 320:#静态演示
        if x < 130 or x > 310:#动态演示
            if x<210:
                userSerial.write(f'AA-{zx_speed}+{zx_speed}M'.encode('utf-8'))
            elif x>320:
                userSerial.write(f'AA+{zx_speed}-{zx_speed}M'.encode('utf-8'))
            pass#转向
        elif d>1.9:
            userSerial.write(f'AA+{qj_speed1}+{qj_speed1}M'.encode('utf-8'))
            pass  # speed1 前进
        elif d>1.19:#1.19m之内再抓取
            userSerial.write(f'AA+{qj_speed2}+{qj_speed2}M'.encode('utf-8'))
            pass  # speed1 前进
        else:
            userSerial.write('AA+00+00M'.encode('utf-8'))
            time.sleep(1)
            RoArm_drive.grab(x,y,d)  # 机械臂到抓取点
            chassis_drive.userSerial.write('AB+0MMMMM'.encode('utf-8'))  # 抓取
            time.sleep(1.5)
            RoArm_drive.down()  # 机械臂到下料点
            chassis_drive.userSerial.write('AB-0MMMMM'.encode('utf-8'))  # 张开
            time.sleep(1.5)
            RoArm_drive.default()  # 机械臂到待机点
            pass#停止
    except Exception:
        print('串口连接失败')

def init():
    global userSerial
    try:
        ########################################################################### 通过串口连接底盘驱动板
        uart_list = list(serial.tools.list_ports.comports())
        if len(uart_list):
            for uart in uart_list:
                if 'CH340' in uart.description:
                    userSerial = serial.Serial(uart.name, 115200, timeout=0.5)
            if userSerial == 0:
                print('底盘驱动板连接失败')
            else:
                print('底盘驱动板连接成功')
        else:
            print('底盘驱动板连接失败')
        ###########################################################################

        userSerial.write('AB-1MMMMM'.encode('utf-8'))#张开爪子

    except Exception:
        print('串口连接出错，没有找到CH340的串口')