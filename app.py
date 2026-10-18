import customtkinter as ctk
import cv2
from ultralytics import YOLO
from PIL import Image, ImageTk
import os
import datetime

# -----------------------------
# Global vars
# -----------------------------
model = None
cap = None
running = False
recording = False
video_writer = None
last_frame = None


# -----------------------------
# Load .pt models from folder
# -----------------------------
def load_models():
    files = os.listdir("models")
    return [f for f in files if f.endswith(".pt")]


# -----------------------------
# Start camera
# -----------------------------
def start_camera():
    global cap, running, model

    selected = model_var.get()
    if selected == "":
        status_label.configure(text="⚠️ Seleziona un modello!")
        return

    model_path = os.path.join("models", selected)
    model = YOLO(model_path)

    # Full HD camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    running = True
    status_label.configure(text=f"Modello attivato: {selected}")

    show_frame()


# -----------------------------
# Stop camera
# -----------------------------
def stop_camera():
    global cap, running, recording, video_writer
    running = False
    recording = False

    if video_writer:
        video_writer.release()
        video_writer = None

    if cap:
        cap.release()

    status_label.configure(text="Videocamera spenta!")


# -----------------------------
# Screenshot
# -----------------------------
def take_screenshot():
    global last_frame

    if last_frame is None:
        return

    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    bgr_frame = cv2.cvtColor(last_frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, bgr_frame)
    status_label.configure(text=f"📸 Screenshot salvato: {filename}")


# -----------------------------
# Start/Stop video recording
# -----------------------------
def toggle_record():
    global recording, video_writer, last_frame

    if not running or last_frame is None:
        return

    if not recording:
        filename = f"record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        h, w, _ = last_frame.shape
        video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (w, h))
        recording = True
        record_btn.configure(text="⏹ Stop")
        status_label.configure(text=f"🎥 Registrazione avviata → {filename}")
    else:
        recording = False
        if video_writer:
            video_writer.release()
            video_writer = None
        record_btn.configure(text="⏺ Record")
        status_label.configure(text="Registrazione finita!")


# -----------------------------
# Show webcam frames + YOLO
# -----------------------------
def show_frame():
    global last_frame, video_writer

    if not running:
        return

    ret, frame = cap.read()
    if not ret:
        return

    # Convert to RGB (fix boja)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Modelo YOLO
    results = model(frame_rgb, verbose=False)
    annotated = results[0].plot()  

    last_frame = annotated

    # Snimanje videa
    if recording and video_writer:
        bgr_frame = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        video_writer.write(bgr_frame)

    # Convert TK
    img = Image.fromarray(annotated)
    imgtk = ImageTk.PhotoImage(img)

    camera_label.imgtk = imgtk
    camera_label.configure(image=imgtk)

    camera_label.after(10, show_frame)


# -----------------------------
# GUI Setup (CustomTkinter)
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("YOLO Detection GUI – Arnel Edition")
app.geometry("1400x900")

FONT = ("Verdana", 15)

# Dropdown modelli
model_var = ctk.StringVar()
models = load_models()

dropdown = ctk.CTkOptionMenu(app, variable=model_var, values=models, width=350, font=FONT)
dropdown.pack(pady=10)

# Dugmad
btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=10)

start_btn = ctk.CTkButton(btn_frame, text="▶ Avvia", command=start_camera, width=140, font=FONT)
start_btn.grid(row=0, column=0, padx=5)

stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", command=stop_camera, width=140, font=FONT)
stop_btn.grid(row=0, column=1, padx=5)

record_btn = ctk.CTkButton(btn_frame, text="⏺ Record", command=toggle_record, width=150, font=FONT)
record_btn.grid(row=0, column=2, padx=5)

shot_btn = ctk.CTkButton(btn_frame, text="📸 Screenshot", command=take_screenshot, width=150, font=FONT)
shot_btn.grid(row=0, column=3, padx=5)

exit_btn = ctk.CTkButton(btn_frame, text="❌ Esci", command=app.destroy, width=140, font=FONT)
exit_btn.grid(row=0, column=4, padx=5)

# Kamerin okvir – POVECAN
camera_label = ctk.CTkLabel(app, text="", width=1280, height=720, fg_color="black")
camera_label.pack(pady=20)

# Status
status_label = ctk.CTkLabel(app, text="Tutto pronto", font=FONT)
status_label.pack(pady=10)

app.mainloop()
