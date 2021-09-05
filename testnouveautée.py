import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import logging
import sys

# create logger
logging.basicConfig(filename='logs.log',format='%(asctime)s - %(name)s - %(levelname)s >>>> %(message)s',level=logging.DEBUG)
logger = logging.getLogger('trakeur de main')
logger.addHandler(logging.StreamHandler(sys.stdout))

from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController

keyboard = Controller()
mouse = MouseController()


##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)
logging.info('camera lancé')
if detector == 1:
    logging.info('main détectée')

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)


    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),(255, 0, 255), 2)
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
            logging.info('mouvement de la souris effectué')

        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                logging.info('clique gauche effectuer')
                autopy.mouse.click()
        if fingers[4]==1:

            # 8.1 Zoom with the fingers
            if fingers[0] == 1 and fingers[1] == 1:
                # 9. Find distance between fingers
                length, img, lineInfo = detector.findDistance(8, 12, img)
                print(length)
                # 10. Click mouse if distance short
                if length <130:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (0, 255, 0), cv2.FILLED)
                    #mouse.press(Button.right)
                    logging.info('zoom avant/scroll vers le bas')
                    mouse.scroll(0, 2)
                    print("Zoom ON")
                elif length > 130:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (255, 0, 0), cv2.FILLED)
                    #mouse.release(Button.right)
                    logging.info('zoom arriere/scroll vers le haut')
                    mouse.scroll(0, -2)

        elif fingers[4]==0:
            print("zoom off")

            if fingers[2]==1:
                keyboard.press(Key.ctrl)
                keyboard.press('l')
                keyboard.release(Key.ctrl)
                keyboard.release('l')
                print("ctrl + l")
                logging.info('ctrl + l effectué')

        if fingers[3]==1:
            keyboard.press(Key.ctrl)
            keyboard.press('s')
            keyboard.release(Key.ctrl)
            keyboard.release('s')
            logging.info('ctrl + s effectué')

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)

if __name__ == "__main__":
  try:
     logger.info('start.py lancé')
  except:
     logger.warning('start.py non lancé')