import sys
import cv2
import numpy as np



if __name__ == "__main__":
    cap = cv2.VideoCapture('test_driving.avi')

    while (cap.isOpened()):
        ret, frame = cap.read()
        cv2.imshow('frame', frame)

        b = np.asarray(frame[:, :, 0], dtype=np.float32)
        g = np.asarray(frame[:, :, 1], dtype=np.float32)
        r = np.asarray(frame[:, :, 2], dtype=np.float32)

        bg = np.absolute(b - g)
        gr = np.absolute(g - r)
        rb = np.absolute(r - b)

        summ = b + g + r
        dif = bg + gr + rb

        mask = np.zeros(np.shape(b), dtype=np.uint8)
        mask[dif < 50] = 255
        mask[summ < 200] = 0

        cv2.imshow('dif mask', mask)

        m_1 = mask[:, :int(width / 2)]
        m_2 = mask[:, int(width / 2):]

        # print("cnt : ", np.sum(m_1 < 1), np.sum(m_2 < 1))

        cnt_1 = np.sum(m_1 < 1)
        cnt_2 = np.sum(m_2 < 1)

        if cnt_1 < 100 or cnt_2 < 100:
            return 0, True


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
