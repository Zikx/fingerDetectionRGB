import numpy as np
import cv2
import math

cap = cv2.VideoCapture(0)

cnt_red = 0
cnt_blue = 0
cnt_green = 0

# def create_rectangle(frame):
#     roi = frame[100:400, 100:400]
#
#     # roi 사각형의 프레임을 그려준다.
#     cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 0)




while(1):
    try:  #an error comes if it does not find anything in window as it cannot find contour of max area
          #therefore this try error statement
        ret, frame = cap.read()
        frame = cv2.flip(frame,1)
        #cv2.dilate에서 사용 할 커널의 크기 - 1값이 되는 외곽의 픽셀크기를 설정
        kernel = np.ones((3, 3), np.uint8)

        # create_rectangle()
        #손인식을 할 범위의 사이즈 (100,100),(400,500) 사각형의 모서리
        roi = frame[100:400, 100:400]

        #roi 사각형의 프레임을 그려준다.
        cv2.rectangle(frame,(100,100),(400,400),(0,255,0),0)

        #roi 범위 안의 색영역추출
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 추출한 색영역과 비교할 범위 (살색) [색범위,채도,명암]

        lower_skin = np.array([0,105,40], dtype=np.uint8)
        upper_skin = np.array([20,255,220], dtype=np.uint8)

    # 추출한 색영역 hsv가 살색 범위만 남긴다.
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # 외곽의 픽셀을 1(흰색)으로 채워 노이즈제거 interations -반복횟수
        mask = cv2.dilate(mask, kernel, iterations = 4)

    #cv2.GaussianBlur 중심에 있는 픽셀에 높은 가중치 -노이즈제거
        mask = cv2.GaussianBlur(mask,(5,5),100)

    #cv2.findContours 경계선 찾기 cv2.RETR_TREE 경계선 찾으며 계층관계 구성 cv2.CHAIN_APPROX_SIMPLE 경계선을 그릴 수 있는 point만 저장
        contours,hierarchy= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.findContours(입력이미지, 검출된 컨투어, 검출된 컨투어의 정보, 검출된 정보를 )

    #경계선 중 최대값 찾기
        cnt = max(contours, key=lambda x: cv2.contourArea(x))

    #엡실론 값에 따라 컨투어 포인트의 값을 줄인다. 각지게 만듬 Douglas-Peucker 알고리즘 이용
        epsilon = 0.0005*cv2.arcLength(cnt,True)
        approx= cv2.approxPolyDP(cnt,epsilon,True)
        M = cv2.moments(cnt)
    #외곽의 점을 잇는 컨벡스 홀
        hull = cv2.convexHull(cnt)

     #컨벡스홀 면적과 외곽면적 정의
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)

    # 컨벡스홀-외곽면적의 비율
        arearatio=((areahull-areacnt)/areacnt)*100

    # cv2.convexityDefects 컨벡스 결함
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

    # 깊이의 개수
        count_finger = 0
    # 시작점, 끝점, 결점을 정한다
        for shape_index in range(defects.shape[0]):  # defects 컨벡스 결함의 수 만큼 반복
            s, e, f, d = defects[shape_index, 0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])
            pt = (100, 180)

            # end,for,start 점의 삼각형 길이
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            s = (a+b+c)/2
            ar = math.sqrt(s*(s-a)*(s-b)*(s-c))

            # 컨벡스 결함으로 이루어진 삼각형에서의 깊이
            d = (2*ar)/a

            # 코사인 법칙을 이용한 손가락 사이 각도
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

            # 각도와 깊이를 확인해 far end start 각점에 표시
            if angle <= 90 and d > 30:
                count_finger += 1
                cv2.circle(roi, far, 6, [255,0,0], -1)
                cv2.circle(roi, end, 6, [255,0,0], 1)
                cv2.circle(roi, start, 6, [0,0,255], 1)

            # 컨벡스홀 라인그리기 start-end로 각각
            cv2.line(roi, start, end, [0, 255, 0], 2)

        topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])  # topmost : 손끝좌표
        cv2.rectangle(roi, (topmost[0]-5, topmost[1]-7), (topmost[0]+5, topmost[1]-2), (0, 255, 0), 0)

        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        cv2.circle(roi, (cx, cy), 6, [255, 0, 0], 1)  # 중점인데 필요없음
        roi2 = frame[100:900, 100:900]
        rgbroi = cv2.cvtColor(roi2, cv2.COLOR_BGR2RGB)

        # find rgb value and print rgb to string

        rgbValueList = rgbroi[topmost[0]-7, topmost[1]]
        cv2.circle(roi, (topmost[0], topmost[1]-15), 4, [0, 100, 100], -1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        if (100 < rgbValueList[0] <= 255) and (rgbValueList[1] < 100) and (rgbValueList[2] < 100):
            cnt_red += 1
            if cnt_red > 1:
                cv2.putText(frame, "Red", (255, 450), font, 1, (255, 255, 255), 2)
                cnt_red = 0
            print("red")
        if(100 < rgbValueList[1] <= 255) and (rgbValueList[0] < 100) and (rgbValueList[2] < 100):
            cnt_green += 1
            if cnt_green > 1:
                cv2.putText(frame, "Green", (255, 450), font, 1, (255, 255, 255), 2)
                cnt_green = 0
            print("GREEN")
        if(100 < rgbValueList[2] <= 255) and (rgbValueList[0] < 100) and (rgbValueList[1] < 100):
            cnt_blue += 1
            if cnt_blue > 1:
                cv2.putText(frame, "Blue", (255, 450), font, 1, (255, 255, 255), 2)
                cnt_blue = 0
            print("BLUE")
        else:
            print("NO COLOR")

        print(rgbValueList[2])
        print('rgb: ', rgbValueList)

        i = 0
        count_finger += 1
        # display corresponding gestures which are in their ranges

        if count_finger == 1:
            if areacnt < 2000:
                cv2.putText(frame, 'Put hand in the box', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                if arearatio < 12:
                    cv2.putText(frame, '0', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

                else:
                    cv2.putText(frame, '1', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        elif count_finger == 2:
            cv2.putText(frame, '2', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        elif count_finger == 3:
            cv2.putText(frame, '3', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        elif count_finger == 4:
            cv2.putText(frame, '4', (0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

        elif count_finger == 5:
            cv2.putText(frame, '5', (0, 50), font, 2, (0,0,255), 3, cv2.LINE_AA)

        elif count_finger == 6:
            cv2.putText(frame, 'reposition', (0, 50), font, 2, (0,0,255), 3, cv2.LINE_AA)

        else:
            cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        # show mask and frame
        cv2.imshow('mask', mask)
        cv2.imshow('frame', frame)

    except:
        pass

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
