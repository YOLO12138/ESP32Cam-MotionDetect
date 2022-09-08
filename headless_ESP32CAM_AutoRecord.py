import numpy as np
import cv2
from datetime import date
import time
TIME = 10 #一次视频录制时常（秒
FPS = 6 #视频帧率
CAM_IP = "192.168.6.118" #ESP摄像头的ip，开机时串口会输出
TotalFrame = FPS*TIME #视频总帧数
Video_Num = 0 #已录制视频数量，初始化为0
sdThresh = 30 #检测物体移动的阈值，越小越灵敏
font = cv2.FONT_HERSHEY_SIMPLEX

def get_date_time():#用时间来给视频文件命名
    time_minute = time.strftime("_%H_%M_%S", time.localtime())
    today = date.today()
    date_yymmdd = today.strftime("%Y%m%d")
    videotitle = date_yymmdd+time_minute
    return date_yymmdd,videotitle

def VideoCapture(videodate,videotitle): #视频捕获
    FPSCount = 0
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(f'clips/{videotitle}.avi', fourcc, FPS, (800,600))

    while(True):
        ret, img = cap.read()
        if FPSCount > TotalFrame:
            break
        out.write(img)
        FPSCount+=1



def distMap(frame1, frame2):
    """outputs pythagorean distance between two frames"""
    frame1_32 = np.float32(frame1)
    frame2_32 = np.float32(frame2)
    diff32 = frame1_32 - frame2_32
    norm32 = np.sqrt(diff32[:,:,0]**2 + diff32[:,:,1]**2 + \
             diff32[:,:,2]**2)/np.sqrt(255**2 + 255**2 + 255**2)
    dist = np.uint8(norm32*255)
    return dist


# cv2.namedWindow('frame')
# cv2.namedWindow('dist')
 
#capture video stream from camera source. 0 refers to first camera, 1 referes to 2nd and so on.
cap = cv2.VideoCapture(f"rtsp://{CAM_IP}:8554/mjpeg/1") #opencv初始化rtsp视频流
print(f"[Camera_Client] Connected with IP {CAM_IP}")

_, frame1 = cap.read()
_, frame2 = cap.read()
 
facecount = 0
while(True):
    _, frame3 = cap.read()
    rows, cols, _ = np.shape(frame3)
    #cv2.imshow('dist', frame3)
    dist = distMap(frame1, frame3)
 
    frame1 = frame2
    frame2 = frame3
 
    # apply Gaussian smoothing
    mod = cv2.GaussianBlur(dist, (9,9), 0)
 
    # apply thresholding
    _, thresh = cv2.threshold(mod, 100, 255, 0)
 
    # calculate st dev test
    _, stDev = cv2.meanStdDev(mod)
 
    # cv2.imshow('dist', mod)
    # cv2.putText(frame2, "Standard Deviation - {}".format(round(stDev[0][0],0)), \
    #             (70, 70), font, 1, (255, 0, 255), 1, cv2.LINE_AA)
    if stDev > sdThresh:
        vidpath_date,timedate = get_date_time()
        print(f"[{timedate}] Start Recording")
        VideoCapture(vidpath_date,timedate)
        Video_Num+=1
        print(f"Video Saved, Total Video Number is {Video_Num}")
        time.sleep(2)


            
 
    #cv2.imshow('frame', frame2)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break
 
cap.release()
cv2.destroyAllWindows()