from flask import Flask, render_template, url_for, request,redirect, Response
import numpy as np
import cv2
from IPython.display import clear_output
url = "http://73.85.164.101:8081/video.mjpg"
staticUrl = "https://dl.dropboxusercontent.com/s/a1qo1e2fsyuxnji/static-video.mp4?dl=0"
target = ''
app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('home.html')
def gen_live(target):
    cam = cv2.VideoCapture(target)
    print('Attempting to open URL')
    if not cam.isOpened():
        raise RuntimeError('Could Not Connect to Cam')
    while True:
        result,frame = cam.read()
        if not result:
            print('Cry')
        frame_enc = cv2.imencode('.jpeg', frame)[1].tobytes()
        yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + frame_enc + b'\r\n')
@app.route('/video_feed')
def video_feed():
    return Response(gen_live(target), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/static', methods=['POST'])
def static_stream():
    global target
    target = staticUrl
    return render_template('base.html', streamtype = "Static Stream")
@app.route('/livestream', methods=['POST'])
def live_stream():
    global target
    target = url
    return render_template('base.html', streamtype ="Livestream")
if __name__ == '__main__':
    app.run()