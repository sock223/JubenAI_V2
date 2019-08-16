import cv2 as cv
import time

WINDOW_NAME = "win"

image = cv.imread("image/img/hai/1.jpg", cv.IMREAD_COLOR)
cv.namedWindow(WINDOW_NAME, cv.WND_PROP_AUTOSIZE)
initialtime = time.time()

cv.startWindowThread()

while (time.time() - initialtime < 5):
  print("in first while")
cv.imshow(WINDOW_NAME, image)
cv.waitKey(1000)

cv.waitKey(1)
cv.destroyAllWindows()
cv.waitKey(1)

initialtime = time.time()
while (time.time() - initialtime < 6):
    print("in second while")