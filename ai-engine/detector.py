import cv2
from ultralytics import YOLO

from logic.sleep_detector import SleepDetector          # Eye-based sleep detection
from logic.sleep_pose_detector import SleepPoseDetector  # Head-down sleep detection


# Load YOLO model (COCO pretrained)
model = YOLO("yolov8n.pt")   # Automatically downloads if missing


def start_detection():
    cap = cv2.VideoCapture(0)

    # Initialize detectors
    sleep_detector = SleepDetector()
    sleep_detector.setup()

    sleep_pose_detector = SleepPoseDetector()  # NEW sleeping-on-table detector

    if not cap.isOpened():
        print("❌ Error: Cannot open webcam")
        return

    print("🔵 AI Engine Running... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # -----------------------------
        # Sleep Detection Logic
        # -----------------------------
        is_sleeping_eye = sleep_detector.detect(frame)        # eyes closed detection
        is_sleeping_pose = sleep_pose_detector.detect(frame)  # head down detection

        if is_sleeping_eye or is_sleeping_pose:
            cv2.putText(frame, "SLEEPING!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        (0, 0, 255), 3)

        # -----------------------------
        # YOLO Object Detection
        # -----------------------------
        results = model(frame, stream=True)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])      # class id
                conf = float(box.conf[0])  # confidence
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                label = model.names[cls]
                color = (0, 255, 0)

                # Draw bounding box for YOLO objects
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                cv2.putText(
                    frame,
                    f"{label} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

        # -----------------------------
        # Display Window
        # -----------------------------
        cv2.imshow("Employee Monitoring - AI Engine", frame)

        # Exit on "q"
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_detection()
