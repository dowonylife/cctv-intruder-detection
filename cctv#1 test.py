#
#      공대선배 라즈베리파이 CCTV 프로젝트 #1 openCV 테스트
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      openCV가 잘 설치되었나 테스트
#
import cv2

img = cv2.imread("lenna.png")
cv2.imshow("Test",img)

img_canny = cv2.Canny(img, 50, 150)
cv2.imshow("Test img Edge", img_canny)

cv2.waitKey(0)
cv2.destroyAllWindows()
