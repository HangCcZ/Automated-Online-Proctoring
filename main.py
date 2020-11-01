import cv2
from fastai.vision.all import load_learner
import numpy as np
import dlib
import time


start = time.time()
detector = dlib.get_frontal_face_detector()
learn_inf = load_learner('/home/hang/PycharmProjects/MaskDetector/venv/models/risk_classifier.pkl')
cap = cv2.VideoCapture("/home/hang/PycharmProjects/MaskDetector/venv/Resources/Hang_video_Nov_1.mp4")

# font
font = cv2.FONT_HERSHEY_SIMPLEX
# fontScale
fontScale = 0.5
# Line thickness of 2 px
thickness = 1

risk_color = {"notCheat": (0, 255, 0), "cheat": (0, 0, 255)}
risk_counter = {"notCheat": 0, "cheat": 0}

prev_time = -1
processed_frames = 0
sample_rate = 1

while True:

    status, img = cap.retrieve(cap.grab())
    # resize image for better processing speed
    img = cv2.resize(img,(960, 540))
    if status:
        # adjust the denominator to skip frames, higher number =  more frame skipping
        time_s = cap.get(cv2.CAP_PROP_POS_MSEC)
        # time_s = cap.get(cv2.CAP_PROP_POS_MSEC)
        if int(time_s) > int(prev_time):
            processed_frames += 1
            # convert to gray for detection processing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()

                # predict result base on the face found in the image
                y_diff = round((y2 - y1) / 1.5)
                x_diff = round((x2 - x1) / 1.5)
                # take face from image only but with some padding
                face_only = img[y1 - y_diff:y2 + y_diff, x1 - x_diff:x2 + x_diff]
                predict_result, label, accuracy = learn_inf.predict(face_only)

                label = label.data.numpy()
                accuracy = (accuracy.data[label]).numpy() * 100

                risk_counter[predict_result] = risk_counter[predict_result] + 1
                #
                message = predict_result + " " + str(round(accuracy, 2))
                # drawing a rectangle and coloring the rectangle based on prediction result
                cv2.rectangle(img, (x1, y1), (x2, y2), risk_color[predict_result], 2)
                cv2.putText(img, message, (x1, y1 + 100), font, fontScale,
                            risk_color[predict_result], thickness, cv2.LINE_AA)
                # scale down from 1080p
            # img = cv2.resize(img, (960, 540))
            cv2.imshow('Video', img)
            if cv2.waitKey(1) & 0XFF == ord('q'):
                break
        prev_time = time_s
    else:
        break

cap.release()
cv2.destroyAllWindows()
end = time.time()
print("With Not Cheat Frames:",risk_counter["notCheat"])
print("Without Cheat Frames:",risk_counter["cheat"])
print("Total time taken to process: {0} second".format(round(end-start,2)))
print("Processed total: {0} frames".format(processed_frames))
print("Average fps:",processed_frames / 20)