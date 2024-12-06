#
#      공대선배 라즈베리파이 CCTV 프로젝트 #3 flask 스트리밍에 글자출력
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      웹캠의 영상을 실시간으로 스트리밍할때, 시분초 표시
#
from flask import Flask, render_template, Response
from PIL import ImageFont, ImageDraw, Image
import datetime
import cv2
import numpy as np

# ngrok 설정
from pyngrok import ngrok


app = Flask(__name__)
capture = cv2.VideoCapture(-1)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
font = ImageFont.truetype('fonts/SCDream6.otf', 18)

def gen_frames():  
    while True:
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
        ref, frame = capture.read()  # 현재 영상을 받아옴
        if not ref:
            break
        else:
            # 이미지를 PIL 형식으로 변환
            frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(frame)
            # REC 텍스트와 빨간 점
            draw.ellipse((10, 10, 30, 30), fill="red")  # 빨간 점
            draw.text((40, 10), "REC", font=font, fill="white")  # REC 텍스트
            # 카메라 이름
            draw.text((frame.width - 110, 10), "말농장 입구", font=font, fill="white")
            # 날짜와 시간
            draw.text((frame.width - 155, frame.height - 20), nowDatetime, font=ImageFont.truetype('fonts/SCDream6.otf', 14), fill="white")
            # 다시 numpy 배열로 변환
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            ref, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index4#4.html') 

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":  # 웹사이트를 호스팅하여 접속자에게 보여주기 위한 부분
    # ngrok 터널 생성
    public_url = ngrok.connect(8080)
    print("ngrok public URL:", public_url)  # 외부에서 접속할 URL 출력
    app.run(host="0.0.0.0", port=8080)
    # host는 현재 라즈베리파이의 내부 IP, port는 임의로 설정
    # 해당 내부 IP와 port를 포트포워딩 해두면 외부에서도 접속가능
