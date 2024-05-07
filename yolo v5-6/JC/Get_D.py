import cv2
import numpy as np
import time
import math

# -----------------------------------双目相机的基本参数---------------------------------------------------------
#   left_camera_matrix          左相机的内参矩阵
#   right_camera_matrix         右相机的内参矩阵
#
#   left_distortion             左相机的畸变系数    格式(K1,K2,P1,P2,0)
#   right_distortion            右相机的畸变系数
# -------------------------------------------------------------------------------------------------------------
# 左镜头的内参，如焦距
left_camera_matrix = np.array([[418.2746,-0.5561,328.6199],[0.,418.9674,251.018],[0.,0.,1.]])
right_camera_matrix = np.array([[418.8376,-0.3231,325.9134],[0.,419.3164,247.1296],[0.,0.,1.]])

# 畸变系数,K1、K2、K3为径向畸变,P1、P2为切向畸变
left_distortion = np.array([[-0.045,0.1544,0.000106268600231475,-0.000176379080122751,0]])
right_distortion = np.array([[-0.0220799115615633,0.0752117528386998,0.000961901527543117,0.000814613413570036,0]])

# 旋转矩阵
R = np.array([[0.9999,-0.0001,-0.0149],
              [0.0002,1.0,0.0063],
              [0.0149,-0.0063,0.9999]])
# 平移矩阵
T = np.array([-120.6048,0.0693,-1.5934])

size = (640, 480)

R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(left_camera_matrix, left_distortion,
                                                                  right_camera_matrix, right_distortion, size, R,
                                                                  T)

# 校正查找映射表,将原始图像和校正后的图像上的点一一对应起来
left_map1, left_map2 = cv2.initUndistortRectifyMap(left_camera_matrix, left_distortion, R1, P1, size, cv2.CV_16SC2)
right_map1, right_map2 = cv2.initUndistortRectifyMap(right_camera_matrix, right_distortion, R2, P2, size, cv2.CV_16SC2)
print(Q)



def get_d(frame,p1,p2):
    # 切割为左右两张图片
    frame1 = frame[0:480, 0:640]
    frame2 = frame[0:480, 640:1280]
    # 将BGR格式转换成灰度图片，用于畸变矫正
    imgL = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    imgR = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # 重映射，就是把一幅图像中某位置的像素放置到另一个图片指定位置的过程。
    # 依据MATLAB测量数据重建无畸变图片,输入图片要求为灰度图
    img1_rectified = cv2.remap(imgL, left_map1, left_map2, cv2.INTER_LINEAR)
    img2_rectified = cv2.remap(imgR, right_map1, right_map2, cv2.INTER_LINEAR)

    # ------------------------------------SGBM算法----------------------------------------------------------
    #   blockSize                   深度图成块，blocksize越低，其深度图就越零碎，0<blockSize<10
    #   img_channels                BGR图像的颜色通道，img_channels=3，不可更改
    #   numDisparities              SGBM感知的范围，越大生成的精度越好，速度越慢，需要被16整除，如numDisparities
    #                               取16、32、48、64等
    #   mode                        sgbm算法选择模式，以速度由快到慢为：STEREO_SGBM_MODE_SGBM_3WAY、
    #                               STEREO_SGBM_MODE_HH4、STEREO_SGBM_MODE_SGBM、STEREO_SGBM_MODE_HH。精度反之
    # ------------------------------------------------------------------------------------------------------
    blockSize = 10
    img_channels = 3
    stereo = cv2.StereoSGBM_create(minDisparity=1,
                                   numDisparities=96,
                                   blockSize=blockSize,
                                   P1=8 * img_channels * blockSize * blockSize,
                                   P2=32 * img_channels * blockSize * blockSize,
                                   disp12MaxDiff=-1,
                                   preFilterCap=1,
                                   uniquenessRatio=10,
                                   speckleWindowSize=100,
                                   speckleRange=100,
                                   mode=cv2.STEREO_SGBM_MODE_HH)
    # 计算视差
    disparity = stereo.compute(img1_rectified, img2_rectified)

    # 卷积核的宽和高
    # k = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    # disparity = cv2.morphologyEx(disparity, cv2.MORPH_CLOSE, k)

    dis_color = disparity
    dis_color = cv2.normalize(dis_color, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)#归一化

    # 计算三维坐标数据值
    threeD = cv2.reprojectImageTo3D(disparity, Q, handleMissingValues=True)


    # 世界坐标 x,y,距离
    # x = (p1[0] + p2[0]) // 2
    # y = (p1[1] + p2[1]) // 2
    # return threeD[y][x][0] * 16 / 1000.0, threeD[y][x][1] * 16/ 1000.0, threeD[y][x][2] * 16/ 1000.0 , dis_color

    #滤波处理
    d_list = []
    x_num = 7  # x被分成x_num份
    y_num = 7  # y被分成y_num份
    x_d = (p2[0] - p1[0]) // x_num  # x步进值
    y_d = (p2[1] - p1[1]) // y_num  # y步进值
    for xn in range(x_num - 1):
        for yn in range(y_num - 1):
            x = (xn + 1) * x_d + p1[0]
            y = (yn + 1) * y_d + p1[1]
            d_list.append(threeD[y][x][2] * 0.016)

    d_list.sort()#将所测所有点的距离升序排序

    return threeD[y][x][0] * 0.016, threeD[y][x][1] * 0.016, d_list[2] , dis_color

