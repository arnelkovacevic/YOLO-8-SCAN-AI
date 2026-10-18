import cv2
import numpy as np
import onnxruntime as ort

model = "yolov8n.onnx"

session = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
img_size = 640

cap = cv2.VideoCapture(0)

def preprocess(frame):
    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, 0)
    return img

while True:
    ret, frame = cap.read()
    if not ret:
        break

    blob = preprocess(frame)
    outputs = session.run(None, {input_name: blob})[0][0]

    for det in outputs:
        x1, y1, x2, y2, score, cls = det[:6]
        if score > 0.5:
            cv2.rectangle(frame, (int(x1), int(y1)),
                          (int(x2), int(y2)), (0, 255, 0), 2)

    cv2.imshow("YOLOv8 Webcam", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
