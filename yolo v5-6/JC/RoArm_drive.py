import requests
import time
import chassis_drive


RoArm_STA_IP = '192.168.137.96'


#下料
#{"T":1041,"x":-210,"y":-50,"z":210,"t":3.14}
down_url1 = f'http://{RoArm_STA_IP}/js?json='+'{%22T%22:1041,%22x%22:-210,%22y%22:-50,%22z%22:210,%22t%22:3.14}'
#{"T":1041,"x":-450,"y":-5,"z":30,"t":3.14}
down_url2 = f'http://{RoArm_STA_IP}/js?json='+'{%22T%22:1041,%22x%22:-450,%22y%22:-5,%22z%22:30,%22t%22:3.14}'
#{"T":1041,"x":-320,"y":-155,"z":20,"t":3.14}
down_url3 = f'http://{RoArm_STA_IP}/js?json='+'{%22T%22:1041,%22x%22:-320,%22y%22:-155,%22z%22:20,%22t%22:3.14}'
#{"T":1041,"x":-300,"y":-1,"z":10,"t":3.14}
down_url4 = f'http://{RoArm_STA_IP}/js?json='+'{%22T%22:1041,%22x%22:-300,%22y%22:-1,%22z%22:10,%22t%22:3.14}'
down_flg = 0
def down():
    try:
        global down_flg
        requests.get(down_url1)
        time.sleep(2)
        if down_flg == 0:
            requests.get(down_url2)
            down_flg = 1
        elif down_flg == 1:
            requests.get(down_url3)
            down_flg = 2
        elif down_flg == 2:
            requests.get(down_url4)
            down_flg = 0
        time.sleep(1.5)
    except Exception:
        print('未连接 RoArm-M2 热点')


#待机:
# {"T":1041,"x":40,"y":0,"z":30,"t":3.14}
default_url = f'http://{RoArm_STA_IP}/js?json='+'{%22T%22:1041,%22x%22:40,%22y%22:0,%22z%22:30,%22t%22:3.14}'
def default():
    try:
        requests.get(default_url)
        time.sleep(1.5)
    except Exception:
        print('未连接 RoArm-M2 热点')

#抓取
# {"T":1041,"x":230,"y":0,"z":210,"t":3.14}
grab_url = f'http://{RoArm_STA_IP}/js?json='+'{%22T%22:1041,'
def grab(x,y,z):
    try:
        RoArm_x = 727.5944707292153*z+-492.3114600190332
        RoArm_y = -2.568695557293277*x+562.0272236265434
        RoArm_z = -2.7863273157738977*y+926.9769162474105
        print('回归拟合得到的机械臂坐标:')
        print( RoArm_x, RoArm_y, RoArm_z)
        print(str(RoArm_x//1), RoArm_y//1, RoArm_z//1)

        v_str = grab_url + f'%22x%22:{RoArm_x},%22y%22:{RoArm_y},%22z%22:{RoArm_z}'+',%22t%22:3.14}'

        requests.get(v_str)
        time.sleep(2.2)
    except Exception:
        print('未连接 RoArm-M2 热点')

