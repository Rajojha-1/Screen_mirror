# screen_share.py
from flask import Flask, Response
import cv2
import mss
import numpy as np

app = Flask(__name__)

def generate_frames():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Capture full screen
        while True:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            frame = cv2.resize(frame, (1280, 720))  # Resize for faster streaming
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return """
        <h1>Live Screen Share</h1>
        <img src='/video' width='100%'>
    """

if __name__ == '__main__':
    # Bind to all network interfaces so Cloudflare can access it
    app.run(host='0.0.0.0', port=8000, threaded=True)
