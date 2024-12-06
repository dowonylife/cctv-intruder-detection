from flask import Flask, render_template, Response
from PIL import ImageFont, ImageDraw, Image
import datetime
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import os
from pyngrok import ngrok

# GPIO 핀 번호 설정
BUTTON_PIN = 15
BUZZER_PIN = 21
LED_PIN = 17

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)  # LED를 꺼진 상태로 초기화
GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)  # 부저도 동일하게 초기화

# GPIO 정리 함수
def cleanup_gpio():
    GPIO.cleanup()

# Flask 앱 초기화
app = Flask(__name__)
capture = cv2.VideoCapture(-1)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
font = ImageFont.truetype('fonts/SCDream6.otf', 18)

# 초기 배경 설정 변수
background = None
alert_active = False
last_alert_time = 0
alert_cooldown = 2  # 경고 재실행 제한 시간 (초)
threshold = 100  # 민감도

# 감지 모드 초기화
detection_enabled = False
button_pressed = False  # 버튼이 눌렸는지 여부를 확인하기 위한 플래그

# 스크린샷 저장 경로
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

# PWM 초기화 (주파수: 440Hz - A4 음)
buzzer_pwm = None

# PWM 초기화 함수
def initialize_pwm():
    global buzzer_pwm
    buzzer_pwm = GPIO.PWM(BUZZER_PIN, 440)

# 움직임이 감지되었을 때 LED와 부저 작동 및 스크린샷 저장 함수
def trigger_alert(frame):
    global alert_active, last_alert_time
    current_time = time.time()

    # 쿨다운 확인
    if alert_active and (current_time - last_alert_time < alert_cooldown):
        return

    alert_active = True
    last_alert_time = current_time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = os.path.join(screenshot_folder, f"{timestamp}.jpg")

    # LED와 부저 활성화 & 스크린샷 저장
    cv2.imwrite(screenshot_path, frame)
    GPIO.output(LED_PIN, GPIO.HIGH)  # LED 켜기
    print("경고: 움직임 감지 감지되었습니다.")

    # 능동 부저 
    for _ in range(4):
        buzzer_pwm.start(50)  # 부저 켜기
        time.sleep(0.25)
        buzzer_pwm.stop()  # 부저 끄기
        time.sleep(0.25)

    # LED 끄기
    GPIO.output(LED_PIN, GPIO.LOW)  # LED 끄기

    alert_active = False

# UI 요소 추가 함수
def add_ui_elements(frame, timestamp):
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)

    # 좌측 상단 REC 및 시각 표시
    if (detection_enabled):
        draw.ellipse((10, 10, 30, 30), fill="red")
        draw.text((40, 10), "DETECTING", font=font, fill="white")
    else:
        draw.ellipse((10, 10, 30, 30), fill="black")
        draw.text((40, 10), "REC", font=font, fill="white")

    # 좌측 하단 현재 시각 표시
    draw.text((frame_pil.width - 135, frame_pil.height - 20), timestamp, font=font, fill="white")

    # 다시 OpenCV 형식으로 변환
    return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

# 스트리밍 및 움직임 감지
def gen_frames():
    global background, detection_enabled, button_pressed
    frame_count = 0
    sampling_rate = 10

    # OpenCV 최적화
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)

    while True:
        # 버튼 상태 확인하여 감지 모드 전환
        if GPIO.input(BUTTON_PIN) == GPIO.LOW and not button_pressed:
            detection_enabled = not detection_enabled
            button_pressed = True
            mode = "활성화" if detection_enabled else "비활성화"
            print(f"감지 모드 {mode}")

        # 버튼을 떼었을 때 플래그 리셋
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH and button_pressed:
            button_pressed = False

        ret, frame = capture.read()
        if not ret:
            break

        frame_count += 1
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

        # 감지 모드가 비활성화된 경우 움직임 감지를 건너뛰고 프레임 스트리밍만 수행
        if not detection_enabled:
            frame = add_ui_elements(frame, nowDatetime)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue

        # 움직임 감지 모드가 활성화된 경우
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if frame_count % sampling_rate == 0:
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # 첫 번째 배경 프레임 설정
            if background is None:
                background = gray
                continue

            # 프레임 차이 계산
            diff = cv2.absdiff(background, gray)
            _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

            # 노이즈 제거 및 컨투어 탐지
            contours, _ = cv2.findContours(cv2.dilate(thresh, None, iterations=2), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            movement_detected = any(cv2.contourArea(contour) > 500 for contour in contours)

            if movement_detected:
                trigger_alert(frame)
                background = gray

        frame = add_ui_elements(frame, nowDatetime)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('html.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    try:
        initialize_pwm()
        public_url = ngrok.connect(8080)
        print("ngrok public URL:", public_url)
        app.run(host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        print("\n프로그램 종료")
    finally:
        cleanup_gpio()