import RPi.GPIO as GPIO
import time

GPIO.cleanup()
# GPIO 핀 번호 설정
BUTTON_PIN = 23  # 버튼 GPIO 핀 번호
BUZZER_PIN = 27  # 부저 GPIO 핀 번호
LED_PIN = 17     # LED GPIO 핀 번호

# GPIO 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 사용
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 버튼 입력 핀, 풀업 저항 활성화
GPIO.setup(BUZZER_PIN, GPIO.OUT)  # 부저 출력 핀 설정
GPIO.setup(LED_PIN, GPIO.OUT)     # LED 출력 핀 설정

# 이벤트 콜백 함수
def button_pressed_callback(channel):
    """버튼이 눌렸을 때 LED와 부저를 2초 동안 켜는 함수"""
    print("버튼 눌림: LED와 부저 활성화 (2초)")

    # 부저와 LED 활성화
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    GPIO.output(LED_PIN, GPIO.HIGH)

    # 2초 동안 상태 유지
    time.sleep(2)

    # 부저와 LED 비활성화
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)

# 버튼 이벤트 감지 설정 (falling 엣지, 채터링 방지)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed_callback, bouncetime=300)

try:
    print("버튼을 눌러 LED와 부저를 테스트하세요 (Ctrl+C로 종료)")
    # 메인 루프
    while True:
        # 메인 루프는 대기 상태로, 이벤트 콜백에 의해 동작이 처리됨
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    GPIO.cleanup()  # GPIO 설정 초기화
