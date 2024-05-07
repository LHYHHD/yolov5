import cv2  # OpenCV库，用于图像和视频处理
import numpy as np  # NumPy库，用于数组和矩阵计算
import torch  # PyTorch库，用于深度学习模型
import time #用于计算实时帧率
from models.experimental import attempt_load  # 导入YOLOv5模型
from utils.general import check_img_size, non_max_suppression, scale_coords  # 导入辅助函数
from utils.plots import Annotator, colors  # 导入辅助函数
from utils.augmentations import letterbox  # 导入辅助函数
from utils.torch_utils import select_device  # 导入辅助函数


from Get_D import get_d
import chassis_drive
import RoArm_drive

# 优化方法:
# 1.重新做线性回归分析
#   1.1 使用多段回归函数
#   1.2 合理划分不同区间段落
# 2.重新校准双目
#线性回归拟合网站: https://nihe.91maths.com/linear.php

weights = '../best.pt'  # 模型权重路径
device = '0'  # 设备号，0表示使用第一个GPU；设置为'cpu'，表示使用CPU
img_size = 640  # 图像大小
stride = 32  # 步长
half = False  # 是否使用半精度浮点数减少内存占用，需要GPU支持

device = select_device(device)  # 设置设备
half &= device.type != 'cpu'  # 如果设备为CPU，则禁用半精度模式

# 导入YOLOv5模型
model = attempt_load(weights, map_location=device)
img_size = check_img_size(img_size, s=stride)  # 检查图像大小是否合法
names = model.names  # 类别名称列表

# 打开摄像头
cap = cv2.VideoCapture(1)  # 0表示打开本地摄像头
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
frame = 0  # 开始处理的帧数

# 获取视频帧率、宽度和高度，设置输出视频的帧率和大小
ret_val, img_all = cap.read()
fps, w, h = 30, img_all.shape[1], img_all.shape[0]
dis_color = img_all[0:480, 0:640]

fps_tim = time.time()

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


chassis_drive.init()#初始化底盘驱动
RoArm_drive.default()#机械臂回到待机点

##############################################注释了底盘和机械臂执行机构、以及底盘初始化中的爪子张开部分、机械臂驱动初始化中的机械臂复位

##############################################
try:
    serial_send_flg = False#串口数据发送标志位(用来在未识别到茄子时，不重复发送)

    # 持续处理视频帧直到退出循环
    while True:

        ret_val, img_all = cap.read()  # 读取视频帧
        img0 = img_all[0:480, 0:640]
        if not ret_val:
            break  # 如果没有读取到帧，则退出循环
        frame += 1  # 帧数自增
        # 对图像进行Padded resize
        img = letterbox(img0, img_size, stride=stride, auto=True)[0]
        # 转换图像格式
        img = img.transpose((2, 0, 1))[::-1]  # HWC转为CHW，BGR转为RGB
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.float() / 255.0  # 像素值归一化到[0.0, 1.0]
        img = img[None]  # [h w c] -> [1 h w c]

        # 模型推理
        pred = model(img)[0]  # 获取模型输出
        pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45, max_det=1000)  # 进行非最大抑制

        # 绘制边框和标签
        det = pred[0]  # 检测结果
        annotator = Annotator(img0.copy(), line_width=3, example=str(names))
        im0 = annotator.result()
        if len(det):
            serial_send_flg = True
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()  # 将边框坐标缩放到原始图像大小
            eggplant_points = []
            for *xyxy, conf, cls in reversed(det):
                c = int(cls)  # 类别索引
                label = f'{names[c]} {conf:.2f}'  # 类别标签和置信度
                if conf > 0.3:  # 置信度大于0.5
                    eggplant_points.append(( int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]) ))
            def takeSecond(elem):
                return elem[0]
            eggplant_points.sort(key=takeSecond)
            if(len(eggplant_points)!=0):
                p1, p2 = (eggplant_points[0][0],eggplant_points[0][1] ), (eggplant_points[0][2],eggplant_points[0][3] )
                zs_x, zs_y, zs_d, dis_color = get_d(img_all, p1, p2)
                # cv2.circle(im0, ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2), 4, (0, 0, 255), -1)
                cv2.rectangle(im0, p1, p2, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

                cv2.putText(im0, f'd:{zs_d:.3f} m', (p1[0], p1[1] - 11), 3, 1, color=(255, 0, 0), thickness=2,
                            lineType=cv2.LINE_AA)
                cv2.putText(im0, f'{label}', (p1[0], p2[1] + 16), 3, 1, color=(0, 0, 255), thickness=2,
                            lineType=cv2.LINE_AA)

                print(f"像素坐标 x:{(p1[0] + p2[0]) // 2},y:{(p1[1] + p2[1]) // 2},直线距离:{zs_d:.3f}m")

                ###################################################显示测距点
                # x_num = 7 #x被分成x_num份
                # y_num = 7 #y被分成y_num份
                # x_d = (p2[0] - p1[0])//x_num #x步进值
                # y_d = (p2[1] - p1[1])//y_num #y步进值
                # for xn in range(x_num-1):
                #     for yn in range(y_num-1):
                #         x=(xn+1)*x_d + p1[0]
                #         y=(yn+1)*y_d + p1[1]
                #         cv2.circle(im0, (x,y), 2, (0, 0, 255), -1)
                ###############################################################

                chassis_drive.control_dp((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2, zs_d)
            else:
                chassis_drive.userSerial.write('AA+00+00M'.encode('utf-8'))
        elif serial_send_flg:
            serial_send_flg = False# 防止视野中没有茄子时重复发送数据
            chassis_drive.userSerial.write('AA+00+00M'.encode('utf-8'))

        FPS = 1 / (time.time() - fps_tim)
        fps_tim = time.time()
        cv2.putText(im0, f'FPS:{FPS:.1f}', (5, 25), 3, 1, color=(0, 255, 0))
        cv2.imshow('image', im0)  # 显示图像
        cv2.imshow('dis_color', dis_color)  # 显示图像

        if cv2.waitKey(1) == ord('q'):
            break
finally:
    # 摄像头对象
    cap.release()
