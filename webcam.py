from ultralytics import YOLO
import cv2

model = YOLO("best-2.pt")  # najmanji i najbrži model

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    annotated = results[0].plot()

    cv2.imshow("YOLOv8 Webcam", annotated)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC za izlaz
        break

cap.release()
cv2.destroyAllWindows()
