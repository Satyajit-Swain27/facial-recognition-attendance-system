import cv2

camera = None

def open_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    return camera

def close_camera():
    global camera
    if camera:
        camera.release()
        camera = None
