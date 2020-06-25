import cv2
import numpy as np
import os
import time
from imutils.perspective import four_point_transform
from imutils import contours
import imutils

# A F B G E C D
DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 0, 1): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    # (0, 1, 1, 1, 0, 1, 0): 4,
    # (1, 1, 0, 1, 0, 1, 1): 5,
    # (1, 1, 0, 1, 1, 1, 1): 6,
    # (1, 0, 1, 0, 0, 1, 0): 7,
    # (1, 1, 1, 1, 1, 1, 1): 8,
    # (1, 1, 1, 1, 0, 1, 1): 9
}

class Detection:
    '''address, stop, obstacle detection class'''

    def __init__(self):
        self.wise = 0
        self.status = 0

        self.ready_flag = False
        self.status_change_flag = False
        self.detect_stop_flag = False
        self.enforce_mode = False
        self.status_detect = False
        self.see_green_flag = False

        self.Green_queue = []  # Green color를 마지막으로 본 뒤, green color가 안보이는 frame check하는 queue
        self.count_frame = 0  # 특정 count가 넘어가면 102랑 202로 status 변경하기 위한 변수
        self.count_stop_frame = 0  # stop을 발견하고 x frame이 지나면 멈추게 하기 위한 변수
        self.count_stop_frame_calc = 0
        self.enforce_frame_count = 0

        self.enforcemode_time_start = 0
        self.stop_time_start = 0
        self.force_update_time_start = 0

        self.queue_data = False
        self.enforce_flag = False
        self.address = ""

    def automatic_brightness_and_contrast(self, image, clip_hist_percent=1):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Calculate grayscale histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_size = len(hist)

        # Calculate cumulative distribution from the histogram
        accumulator = []
        accumulator.append(float(hist[0]))
        for index in range(1, hist_size):
            accumulator.append(accumulator[index - 1] + float(hist[index]))

        # Locate points to clip
        maximum = accumulator[-1]
        clip_hist_percent *= (maximum / 100.0)
        clip_hist_percent /= 2.0

        # Locate left cut
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1

        # Locate right cut
        maximum_gray = hist_size - 1
        while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
            maximum_gray -= 1

        # Calculate alpha and beta values
        alpha = 255 / (maximum_gray - minimum_gray)
        beta = -minimum_gray * alpha


        auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return (auto_result, alpha, beta)

    def adjust_gamma(self, image, gamma=1.0):
        # build a lookup table mapping the pixel values [0, 255] to
        # their adjusted gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
                          for i in np.arange(0, 256)]).astype("uint8")

        # apply gamma correction using the lookup table
        return cv2.LUT(image, table)

    def define_stop_range(self, image):
        mark = image.copy()
        #  BGR 제한 값 설정
        blue_lower_threshold = 20  # 10
        green_lower_threshold = 20  # 10
        red_lower_threshold = 20  # 10
        bgr_lower_threshold = [blue_lower_threshold, green_lower_threshold, red_lower_threshold]

        #  BGR 제한 값 설정
        blue_upper_threshold = 200  # 140
        green_upper_threshold = 200  # 160
        red_upper_threshold = 200  # 140
        bgr_upper_threshold = [blue_upper_threshold, green_upper_threshold, red_upper_threshold]

        # BGR 제한 값보다 크면 흰색색으로
        thresholds = (image[:, :, 0] < bgr_lower_threshold[0]) \
                     | (image[:, :, 1] < bgr_lower_threshold[1]) \
                     | (image[:, :, 0] > bgr_upper_threshold[0]) \
                     | (image[:, :, 1] > bgr_upper_threshold[1]) \


        mark[thresholds] = [0, 0, 0]
        # cv2.imshow("mark", mark)
        # cv2.waitKey(0)
        LAB = cv2.cvtColor(mark, cv2.COLOR_BGR2LAB)
        L,A,B=cv2.split(LAB)

        A = cv2.inRange(A,127,255)
        address = cv2.bitwise_and(LAB, LAB, mask=A)
        address = cv2.cvtColor(address, cv2.COLOR_LAB2BGR)
        gray = cv2.cvtColor(address, cv2.COLOR_BGR2GRAY)

        # threshold the warped image, then apply a series of morphological
        # operations to cleanup the thresholded image
        img = cv2.threshold(gray, 0, 255,
                            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        img = cv2.bitwise_not(img)
        # cv2.imshow("img", img)
        # cv2.waitKey(0)

        return img

    def define_add_range(self, image):
        mark = np.copy(image)
        #  BGR 제한 값 설정
        blue_lower_threshold = 10  # 10
        green_lower_threshold = 10  # 10
        red_lower_threshold = 10  # 10
        bgr_lower_threshold = [blue_lower_threshold, green_lower_threshold, red_lower_threshold]

        #  BGR 제한 값 설정
        blue_upper_threshold = 220  # 140
        green_upper_threshold = 220  # 160
        red_upper_threshold = 220  # 140
        bgr_upper_threshold = [blue_upper_threshold, green_upper_threshold, red_upper_threshold]

        # BGR 제한 값보다 크면 흰색색으로
        thresholds = (image[:, :, 0] < bgr_lower_threshold[0]) \
                     | (image[:, :, 1] < bgr_lower_threshold[1]) \
                     | (image[:, :, 0] > bgr_upper_threshold[2]) \
                     | (image[:, :, 0] > bgr_upper_threshold[0]) \
                     | (image[:, :, 1] > bgr_upper_threshold[1]) \
                     | (image[:, :, 2] > bgr_upper_threshold[2])

        mark[thresholds] = [0, 0, 0]

        #  BGR 제한 값 설정
        blue_lower_threshold = 20  # 10
        green_lower_threshold = 20  # 10
        red_lower_threshold = 20  # 10
        bgr_lower_threshold = [blue_lower_threshold, green_lower_threshold, red_lower_threshold]

        #  BGR 제한 값 설정
        blue_upper_threshold = 200  # 140
        green_upper_threshold = 200  # 160
        red_upper_threshold = 200  # 140
        bgr_upper_threshold = [blue_upper_threshold, green_upper_threshold, red_upper_threshold]

        # BGR 제한 값보다 크면 흰색색으로
        thresholds = (mark[:, :, 0] < bgr_lower_threshold[0]) \
                     | (mark[:, :, 1] < bgr_lower_threshold[1]) \
                     | (mark[:, :, 0] > bgr_upper_threshold[0]) \
                     | (mark[:, :, 1] > bgr_upper_threshold[1]) \


        mark[thresholds] = [0, 0, 0]
        # cv2.imshow('mark', mark)  # 이미지 출력
        # cv2.waitKey(0)
        LAB = cv2.cvtColor(mark, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(LAB)
        A = cv2.inRange(A, -80, 115)

        return A

    def find_stop(self, image, mask):
        ori_img = image.copy()

        contour, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ## If there is no a red region, empty list returns
        if contour:
            for cnt in contour:
                area = cv2.contourArea(cnt)
                epsilon = 0.03 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                sizeapp = len(approx)
                if area > 10000 and epsilon < 26 and sizeapp>5:

                    if self.wise == 0:
                        if self.status == 6 and not self.detect_stop_flag:
                            self.detect_stop_flag = True
                    elif self.wise == 1:
                        if self.status == 1 and not self.detect_stop_flag:
                            self.detect_stop_flag = True
                    else:
                        pass

        return ori_img

    def find_address(self, image, mask):
        self.queue_data = False
        self.see_green_flag = False

        ori_img = image.copy()
        image, alpha, beta = self.automatic_brightness_and_contrast(image)
        image = self.adjust_gamma(image, gamma=1.2)

        contour, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contour:
            for cnt in contour:
                area = cv2.contourArea(cnt)
                epsilon = 0.03 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                sizeapp = len(approx)

                if area > 2700 and area < 7500 and epsilon < 17 and epsilon > 5:
                    if sizeapp is not 4:
                        pass
                    else:
                        displayCnt = approx
                        temp = displayCnt.reshape(4, 2)
                        cropped = four_point_transform(image, temp)
                        y=[]
                        for i in range(len(temp)):
                            y.append(temp[i][1])
                        y.sort()
                        middle_line = ((temp[0][1] + temp[1][1]+temp[2][1] + temp[3][1])/4-y[0])*2

                        # cv2.imshow("img", img)
                        # cv2.waitKey(0)

                        if cropped.shape[0] == 0 or cropped.shape[1] == 0:
                            pass
                        else:
                            self.see_green_flag = True
                            self.queue_data = True
                            image = cv2.dilate(cropped, (5, 5), iterations=4)
                            image = cv2.erode(image, (5, 5), iterations=5)
                            image = self.adjust_gamma(image, gamma=0.5)
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                            img = cv2.threshold(gray, 0, 255,
                                                cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                            thresh = cv2.erode(img, (5, 5), iterations=2)
                            ROI_image = cv2.bitwise_not(thresh)
                            # cv2.imshow("ROI_image", ROI_image)
                            # cv2.waitKey(0)

                            x, y, w, h = cv2.boundingRect(displayCnt)
                            cv2.rectangle(ori_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
                            cnts = cv2.findContours(ROI_image.copy(), cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)
                            cnts = imutils.grab_contours(cnts)
                            digitCnts = []

                            # loop over the digit area candidates
                            for c in cnts:
                                # compute the bounding box of the contour
                                (x, y, w, h) = cv2.boundingRect(c)
                                # print(cv2.boundingRect(c))

                                # if the contour is sufficiently large, it must be a digit
                                if w < 30 and w > 1 and h > 10:
                                    digitCnts.append(c)
                                    # print("digit area", cv2.boundingRect(c))

                            if not digitCnts:
                                #print("This is not address")
                                pass
                            else:
                                digitCnts = contours.sort_contours(digitCnts,
                                                                   method="left-to-right")[0]
                                digits = []
                                # loop over each of the digits
                                for c in digitCnts:
                                    # extract the digit ROI
                                    (x, y, w, h) = cv2.boundingRect(c)
                                    # print("before digit", (x, y, w, h))

                                    if w < 15:
                                        if x < 25:
                                            w = x + w
                                            x = x - x
                                        else:
                                            w = 20
                                            x = x - w + 5
                                    # print("after digit", (x, y, w, h))
                                    roi = ROI_image[y:y + h, x:x + w]

                                    # compute the width and height of each of the 7 segments
                                    # we are going to examine
                                    (roiH, roiW) = roi.shape

                                    (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
                                    dHC = int(roiH * 0.05)

                                    # define the set of 7 segments
                                    segments = [
                                        ((0, 0), (w, dH)),  # top
                                        ((0, 0), (dW, h // 2)),  # top-left
                                        ((w - dW, 0), (w, h // 2)),  # top-right
                                        ((0, (h // 2) - dHC), (w, (h // 2) + dHC)),  # center
                                        ((0, h // 2), (dW, h)),  # bottom-left
                                        ((w - dW, h // 2), (w, h)),  # bottom-right
                                        ((0, h - dH), (w, h))  # bottom
                                    ]
                                    on = [0] * len(segments)

                                    # loop over the segments
                                    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
                                        segROI = roi[yA:yB, xA:xB]

                                        total = cv2.countNonZero(segROI)
                                        area = (xB - xA) * (yB - yA)
                                        if float(area) == 0:
                                            pass
                                        elif (total / float(area) > 0.4):
                                            on[i] = 1
                                    if tuple(on) in DIGITS_LOOKUP.keys():
                                        digit = DIGITS_LOOKUP[tuple(on)]
                                        digits.append(str(digit))
                                self.address = "".join(digits)

                                if len(self.address) == 0:
                                    pass
                                elif len(self.address) is 3:
                                    #print("middle_line",middle_line)
                                    if middle_line > 55:
                                        if self.wise == 0:
                                            if self.address == "102" and self.status == 1:
                                                self.status = 1
                                                self.enforce_flag = True
                                            elif self.address == "202" and self.status == 4:
                                                self.status = 4
                                                self.enforce_flag = True
                                        elif self.wise == 1:
                                            if self.address == "102"  and self.status == 3:
                                                self.status = 3
                                                self.enforce_flag = True
                                            elif self.address == "202" and self.status == 6:
                                                self.status = 6
                                                self.enforce_flag = True
                                    else:
                                        pass

        # print("#############address#############", address)
        # print("#####QUEUE DATA#####",queue_data)

        cv2.putText(ori_img, self.address, (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    (0, 255, 0), 2)

        return ori_img

    def find_object(self, image, curr_orientation):
        if curr_orientation == 'c':
            self.wise = 1
        else:
            self.wise = 0
        self.address = None
        address_mask = self.define_add_range(image)
        stop_mask = self.define_stop_range(image)
        image = self.find_address(image, address_mask)
        ori_img = self.find_stop(image, stop_mask)

        return ori_img

    def detect_flag(self, image, curr_orientation):
        if curr_orientation == 'c':
            self.wise = 1
        else:
            self.wise = 0

        if self.detect_stop_flag:
            if self.count_stop_frame == 0:
                self.stop_time_start = time.time()
            self.count_stop_frame += 1
            if (time.time() - self.stop_time_start) > 1.5:
                if self.wise == 0:
                    self.status += 1
                    self.status = self.status % 7
                    self.status_detect = True
                else:
                    self.status -= 1
                    self.status = self.status % 7
                    self.status_detect = True
                self.detect_stop_flag = False
                self.count_stop_frame = 0
                self.stop_time_start = time.time()
        elif not self.detect_stop_flag:
            if self.wise == 0:
                if self.status == 6:  # 201 지나면서 count 시작
                    if self.count_stop_frame_calc == 0:
                        self.stop_time_start = time.time()
                    self.count_stop_frame_calc += 1
                    if (time.time() - self.stop_time_start) > 1.5:
                        self.status += 1  # 102 status
                        self.status = self.status % 7
                        self.status_detect = True
                        self.count_stop_frame_calc = 0
                        self.stop_time_start = time.time()
                else:
                    pass

            elif self.wise == 1:
                if self.status == 1:  # 101 지나면서 count 시작
                    if self.count_stop_frame_calc == 0:
                        self.stop_time_start = time.time()
                    self.count_stop_frame_calc += 1
                    if (time.time() - self.stop_time_start) > 2:
                        self.status -= 1  # 102 status
                        self.status = self.status % 7
                        self.status_detect = True
                        self.count_stop_frame_calc = 0
                        self.stop_time_start = time.time()
                else:
                    pass
            else:
                pass
        else:
            pass

        if self.enforce_flag:
            self.enforce_mode = True
        else:
            pass
        if self.enforce_mode:
            if self.enforce_frame_count == 0:
                print("Enforce mode on")
                self.enforcemode_time_start = time.time()
            self.enforce_frame_count += 1
            if (time.time() - self.enforcemode_time_start) > 0.4:
                self.enforce_mode = False
                self.enforce_flag = False
                if self.wise == 0:
                    self.status += 1
                else:
                    self.status -= 1
                self.status = self.status % 7
                self.status_detect = True
                self.enforcemode_time_start = time.time()

            print("enforce_frame_count::", self.enforce_frame_count)
        else:
            # print("Enforce mode off")
            if self.see_green_flag: #초록색이 보이면 on
                self.ready_flag = True
                del self.Green_queue[:] #초록색이 보이면 queue 내용 비우기

            if self.ready_flag and not self.queue_data:
                self.Green_queue.append(self.queue_data)
            if len(self.Green_queue) > 14:
                self.status_change_flag = True

            ## status_change_flag가 True일 때, 운행 방향에 따라 status가 바뀌는 부분
            if self.status_change_flag:
                if self.wise == 0:
                    self.status += 1
                    self.status = self.status % 7
                    self.status_detect = True
                elif self.wise == 1:
                    self.status -= 1
                    self.status = self.status % 7
                    self.status_detect = True

            ### 102, 202 못봤을 경우를 위한 status 강제 update code ###
            #print("time : ", time.time() - self.force_update_time_start)
            if self.wise == 0:  # clock-wise
                if (self.status == 1 and not self.ready_flag):  # 101 지나면서 count 시작
                    if self.count_frame == 0:
                        self.force_update_time_start = time.time()
                    self.count_frame += 1
                if (self.status == 4 and not self.ready_flag):  # 203 지나면서 count 시작
                    if self.count_frame == 0:
                        self.force_update_time_start = time.time()
                    self.count_frame += 1
                if self.status == 1 and (time.time() - self.force_update_time_start > 3) and not self.ready_flag:
                    self.status += 1  # 102 status
                    self.status = self.status % 7
                    self.status_detect = True
                    self.count_frame = 0
                    self.force_update_time_start = time.time()
                # if count_frame > 330 and not ready_flag:
                if self.status == 4 and (time.time() - self.force_update_time_start > 3.5) and not self.ready_flag:
                    self.status += 1  # 202 status
                    self.status = self.status % 7
                    self.status_detect = True
                    self.count_frame = 0
                    self.force_update_time_start = time.time()
            elif self.wise == 1:  # counter-clock-wise
                if (self.status == 6 and not self.ready_flag):  # 201 지나면서 count 시작
                    if self.count_frame == 0:
                        self.force_update_time_start = time.time()
                    self.count_frame += 1
                elif (self.status == 3 and not self.ready_flag):  # 103 지나면서 count 시작
                    if self.count_frame == 0:
                        self.force_update_time_start = time.time()
                    self.count_frame += 1
                if self.status == 6 and (time.time() - self.force_update_time_start > 3.5) and not self.ready_flag:
                    self.status -= 1  # 202 status
                    self.status = self.status % 7
                    self.status_detect = True
                    self.count_frame = 0
                    self.force_update_time_start = time.time()
                if self.status == 3 and (time.time() - self.force_update_time_start > 3) and not self.ready_flag:
                    self.status -= 1  # 102 status
                    self.status = self.status % 7
                    self.status_detect = True
                    self.count_frame = 0
                    self.force_update_time_start = time.time()
            else:
                pass

        if self.status_detect:
            del self.Green_queue[:]
            
            self.see_green_flag = False
            self.ready_flag = False
            self.status_change_flag = False
            self.detect_stop_flag = False
            
            self.count_frame = 0
            
            self.enforcemode_time_start = time.time()
            self.stop_time_start = time.time()
            self.force_update_time_start = time.time()

        #print("##########################state####################",self.status)
        #print("enforcemode_time_start::",time.time()-self.enforcemode_time_start)
        #print("stop_time_start::", time.time()-self.stop_time_start)
        #print("force_update_time_start::", time.time()-self.force_update_time_start)


        cv2.putText(image, self.address, (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    (0, 255, 0), 2)
        cv2.putText(image, "status:" + str(self.status), (450, 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                                           (255, 0, 0), 4)

        return image
