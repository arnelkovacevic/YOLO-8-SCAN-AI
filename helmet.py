from ultralytics import YOLO
import cv2

# --- Load models ---
model_person = YOLO("yolov8n.pt")  # generalni model za osobe
model_ppe    = YOLO("best.pt")     # PPE model (Helmet / No Helmet)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -----------------------
    # 1) DETEKTUJ PERSON
    # -----------------------
    person_results = model_person(frame, verbose=False)[0]

    persons = []
    for box, cls in zip(person_results.boxes.xyxy, person_results.boxes.cls):
        if int(cls) == 0:  # class 0 = person
            x1, y1, x2, y2 = map(int, box)
            persons.append((x1, y1, x2, y2))

    # -----------------------
    # 2) DETEKTUJ HELMET / NO-HELMET
    # -----------------------
    ppe_results = model_ppe(frame, verbose=False)[0]

    ppe_boxes = []
    for box, cls in zip(ppe_results.boxes.xyxy, ppe_results.boxes.cls):
        x1, y1, x2, y2 = map(int, box)
        english_label = ppe_results.names[int(cls)]  # Helmet / No Helmet

        # Prevedi na talijanski
        if english_label == "Helmet":
            label = "Casco"
        elif english_label == "No Helmet":
            label = "Senza Casco"
        else:
            label = english_label

        ppe_boxes.append((x1, y1, x2, y2, label))

    # -----------------------
    # 3) SPOJI PERSON + PPE
    # -----------------------
    annotated = frame.copy()

    for (px1, py1, px2, py2) in persons:
        person_center_x = (px1 + px2) // 2
        person_center_y = (py1 + py2) // 2

        helmet_status = "Sconosciuto"
        color = (0, 255, 255)  # žuto dok ne znamo

        for (hx1, hy1, hx2, hy2, helmet_type) in ppe_boxes:
            # provjera da li helmet bounding box dodiruje osobu
            if hx1 < person_center_x < hx2 and hy1 < person_center_y < hy2:
                helmet_status = helmet_type
                break

        if helmet_status == "Casco":
            color = (0, 255, 0)       # zeleno = ima kacigu
        elif helmet_status == "Senza Casco":
            color = (0, 0, 255)       # crveno = nema kacigu

        cv2.rectangle(annotated, (px1, py1), (px2, py2), color, 2)
        cv2.putText(
            annotated,
            f"Persona: {helmet_status}",
            (px1, py1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    # -----------------------
    # PRIKAZ
    # -----------------------
    cv2.imshow("Smart YOLO PPE Detection", annotated)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC za izlaz
        break

cap.release()
cv2.destroyAllWindows()
