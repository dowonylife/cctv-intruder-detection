# CCTV Intruder Detection System with Raspberry Pi

## 프로젝트 설명
이 프로젝트는 라즈베리 파이를 사용하여 CCTV 기반의 도둑 감지 시스템을 구현한 것입니다. 버튼을 누르면 감지 모드가 활성화되어, CCTV 화면에서 움직임을 감지할 수 있습니다. 움직임이 감지되면 LED와 부저가 활성화되고, 스크린샷이 저장됩니다. 또한, 실시간으로 웹 스트리밍을 통해 CCTV 화면을 확인할 수 있습니다.

## 요구사항

### 하드웨어:
- 라즈베리 파이
- 버튼 (GPIO 15 핀에 연결)
- LED (GPIO 17 핀에 연결)
- 부저 (GPIO 21 핀에 연결)
- 카메라 모듈 (USB 웹캠 또는 라즈베리 파이 카메라 모듈)
- (선택 사항) 외부 인터넷 연결을 위한 네트워크

### 소프트웨어:
- Python 3.x
- Flask
- OpenCV
- Pillow
- pyngrok (ngrok을 사용해 외부에서 접근할 수 있도록 웹 서버를 터널링)

## 설치 방법

### 1. 라즈베리 파이 환경 설정
라즈베리 파이에 필요한 라이브러리를 설치해야 합니다.

```bash
sudo apt update
sudo apt install python3-pip
sudo apt install python3-opencv
sudo apt install python3-pillow
sudo apt install python3-flask
sudo apt install libatlas-base-dev
pip3 install pyngrok
