import numpy as np
import cv2


def inventoryGraphic(red_num, blue_num, green_num):
    hpos = 150
    vpos = 0
    img1 = np.zeros((400, 512, 3), np.uint8) + 255
    img1 = cv2.rectangle(img1, (50, 250), (100, 300), (0, 0, 255), -1)
    img1 = cv2.rectangle(img1, (200, 250), (250, 300), (255, 0, 0), -1)
    img1 = cv2.rectangle(img1, (350, 250), (400, 300), (0, 255, 0), -1)
    cv2.putText(img1, 'Inventory', (100, 190), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(red_num), (110, 285), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(blue_num), (260, 285), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(green_num), (410, 285), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    img2 = cv2.imread("white.png")

    # img2 resize해준다.
    width = int(img2.shape[0] * 0.3)
    height = int(img2.shape[1] * 0.1)
    img2 = cv2.resize(img2, (width, height))

    # 이미지의 가로길이 세로길이 가져온다.
    rows, cols, channel = img2.shape
    # 입력받은 roi지정
    roi = img1[vpos:vpos + rows, hpos: hpos + cols]

    # 마스크 만들기
    img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)

    # 0이면 그대로 두고 아니면 그대로 mask를 씌웁니다.
    img2_fg = cv2.bitwise_and(img2, img2, mask=mask)

    # 두 이미지를 더해서 검은 부분과 색이 있는 부분이 더해져서 없어집니다.
    img1[vpos: vpos + rows, hpos: hpos + cols] = img2_fg

    return img1


def loadDeactivateGraphic():
    img1 = np.zeros((200, 500, 3), np.uint8) + 0
    cv2.putText(img1, '- Load - ', (100, 110), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 2)
    return img1

def InventoryBatteryDeactivateGraphic():
    img1 = np.zeros((200, 500, 3), np.uint8) + 0
    cv2.putText(img1, '- Inventory/Battery - ', (60, 110), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img1

def InventoryActivateGraphic():
    img1 = np.zeros((200, 500, 3), np.uint8) + 0
    img1[:, :, 0] += 255
    img1[:, :, 1] += 255
    img1[:, :, 2] += 25
    cv2.putText(img1, '- Refill Inventory! - ', (60, 110), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    return img1

def BatteryActivateGraphic():
    img1 = np.zeros((200, 500, 3), np.uint8) + 0
    img1[:, :, 0] += 25
    img1[:, :, 1] += 255
    img1[:, :, 2] += 255
    cv2.putText(img1, '- Change Battery! - ', (70, 110), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    return img1

def loadGraphic(red_num, blue_num, green_num):
    img1 = np.zeros((200, 500, 3), np.uint8) + 255
    img1 = cv2.rectangle(img1, (50, 120), (100, 170), (0, 0, 255), -1)
    img1 = cv2.rectangle(img1, (200, 120), (250, 170), (255, 0, 0), -1)
    img1 = cv2.rectangle(img1, (350, 120), (400, 170), (0, 255, 0), -1)
    cv2.putText(img1, 'Load list', (100, 70), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(red_num), (100, 155), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(blue_num), (250, 155), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(green_num), (400, 155), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # img2 = cv2.imread("white.png")

    # img2 resize해준다.
    # width = int(img2.shape[0] * 0.3)
    # height = int(img2.shape[1] * 0.1)
    # img2 = cv2.resize(img2, (width, height))

    # 이미지의 가로길이 세로길이 가져온다.
    # rows, cols, channel = img2.shape
    # 입력받은 roi지정
    # roi = img1[vpos:vpos + rows, hpos: hpos + cols]

    # 마스크 만들기
    # img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)

    # 0이면 그대로 두고 아니면 그대로 mask를 씌웁니다.
    # img2_fg = cv2.bitwise_and(img2, img2, mask=mask)

    # 두 이미지를 더해서 검은 부분과 색이 있는 부분이 더해져서 없어집니다.
    # img1[vpos: vpos + rows, hpos: hpos + cols] = img2_fg

    return img1
    # cv2.imshow("Load", img1)
    # cv2.waitKeyEx(0)
    # cv2.destroyAllWindows()


def unloadDeactivateGraphic():
    img1 = np.zeros((200, 500, 3), np.uint8) + 0
    cv2.putText(img1, '- Unload - ', (70, 110), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 2)
    return img1


def unloadGraphic(address, red_num, blue_num, green_num):
    img1 = np.zeros((200, 500, 3), np.uint8) + 255
    img1 = cv2.rectangle(img1, (50, 120), (100, 170), (0, 0, 255), -1)
    img1 = cv2.rectangle(img1, (200, 120), (250, 170), (255, 0, 0), -1)
    img1 = cv2.rectangle(img1, (350, 120), (400, 170), (0, 255, 0), -1)
    cv2.putText(img1, 'Unload list', (90, 70), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 2)
    cv2.putText(img1, 'Address: ' + str(address), (110, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(red_num), (100, 155), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(blue_num), (250, 155), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img1, 'X ' + str(green_num), (400, 155), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # img1 = np.zeros((400, 300, 3), np.uint8) + 255
    # img1 = cv2.rectangle(img1, (50, 250), (100, 300), (0, 0, 255), -1)
    # img1 = cv2.rectangle(img1, (200, 250), (250, 300), (255, 0, 0), -1)
    # img1 = cv2.rectangle(img1, (350, 250), (400, 300), (0, 255, 0), -1)
    # cv2.putText(img1, 'unload list', (100,170), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 2)
    # cv2.putText(img1, 'Address: ' + str(address), (110,220), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 2)
    # cv2.putText(img1, 'X ' + str(red_num), (110, 285), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # cv2.putText(img1, 'X ' + str(blue_num), (260, 285), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # cv2.putText(img1, 'X ' + str(green_num), (410, 285), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # img2 = cv2.imread("white.png")
    # # img2 resize해준다.
    # width = int(img2.shape[0] * 0.3)
    # height = int(img2.shape[1] * 0.1)
    # img2 = cv2.resize(img2, (width, height))
    #
    # # 이미지의 가로길이 세로길이 가져온다.
    # rows, cols, channel = img2.shape
    # # 입력받은 roi지정
    # roi = img1[vpos:vpos + rows, hpos: hpos + cols]
    #
    # # 마스크 만들기
    # img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
    #
    # # 0이면 그대로 두고 아니면 그대로 mask를 씌웁니다.
    # img2_fg = cv2.bitwise_and(img2, img2, mask=mask)
    #
    # # 두 이미지를 더해서 검은 부분과 색이 있는 부분이 더해져서 없어집니다.
    # img1[vpos: vpos + rows, hpos: hpos + cols] = img2_fg
    # cv2.imshow("Unload", img1)
    # cv2.waitKeyEx(0)
    # cv2.destroyAllWindows()

    return img1

def unloadPassGraphic():
    img1 = np.zeros((200, 500, 3), np.uint8) + 0
    cv2.putText(img1, '- Unload Pass - ', (40, 110), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
    return img1

def MaintenanceOn():
    img1 = np.zeros((200, 500, 3), np.uint8)
    img1[:, :, 2] += 255
    cv2.putText(img1, '- Maintenance Mode On - ', (25, 110), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    return img1

def MaintenanceOff():
    img1 = np.zeros((200, 500, 3), np.uint8)
    img1[:, :, 1] += 255
    cv2.putText(img1, '- Maintenance Mode Off - ', (25, 110), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    return img1


# img = InventoryActivateGraphic()
# cv2.imshow("Unload", img)
# cv2.waitKeyEx(0)
# cv2.destroyAllWindows()
