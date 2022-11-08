from sys import stdout
import cv2


findshirtC = cv2.imread(
            'CheckImages//Default//86C.png', cv2.IMREAD_GRAYSCALE)
resC = cv2.matchTemplate(screen, findshirtC, cv2.TM_CCOEFF_NORMED)
print(findshirtC)