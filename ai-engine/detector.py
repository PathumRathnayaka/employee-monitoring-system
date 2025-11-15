import cv2
from ultralytics import YOLO

# Load YOLO model (COCO pretrained)
model = YOLO("yolov8n.pt")   # Automatically downloads if not available

def start_detection():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    print("🔵 AI Engine Running... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO detection
        results = model(frame, stream=True)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])     # class id
                conf = float(box.conf[0]) # confidence
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw detections
                color = (0, 255, 0)
                label = model.names[cls]

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, color, 2)

        cv2.imshow("Employee Monitoring - AI Engine", frame)

        # quit on key (q)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_detection()
