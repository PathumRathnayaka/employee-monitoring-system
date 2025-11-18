import cv2
from ultralytics import YOLO
import threading
import time

from ai_engine.logic.sleep_detector import SleepDetector
from ai_engine.logic.sleep_pose_detector import SleepPoseDetector
from ai_engine.logic.phone_detector import PhoneDetector
from ai_engine.logic.away_detector import AwayDetector

from backend.services.event_logger import EventLogger

# Load YOLO model (COCO pretrained)
model = YOLO("yolov8n.pt")


class DetectionRunner:
    def __init__(self, show_preview=True):  # Changed default to True
        self.running = False
        self.cap = None
        self.show_preview = show_preview
        self.frame_count = 0
        self.current_alerts = []  # Store active alerts

    def start(self):
        """Start detection in a separate thread"""
        if self.running:
            print("⚠️  Detection already running!")
            return

        self.running = True
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("❌ Error: Cannot open webcam")
            self.running = False
            return

        # Initialize detectors
        self.sleep_detector = SleepDetector()
        self.sleep_detector.setup()
        self.sleep_pose_detector = SleepPoseDetector()
        self.phone_detector = PhoneDetector()
        self.away_detector = AwayDetector()

        # Event logger
        self.logger = EventLogger(employee_id="001")

        print("=" * 60)
        print("🔵 AI Engine Started")
        print("📹 Webcam: Active")
        print("🔌 SocketIO: Ready to emit events")
        if self.show_preview:
            print("🎥 Preview mode: Window will open")
        print("=" * 60)

    def process_frame(self):
        """Process a single frame"""
        if not self.running or not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        self.frame_count += 1

        # Sleep Detection
        is_sleeping_eye = self.sleep_detector.detect(frame)
        is_sleeping_pose = self.sleep_pose_detector.detect(frame)
        is_sleeping = is_sleeping_eye or is_sleeping_pose

        if is_sleeping:
            cv2.putText(frame, "SLEEPING!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        (0, 0, 255), 3)

        # Log sleep event
        self.logger.handle_event("sleep", is_sleeping)

        # YOLO Object Detection
        results = model(frame, stream=True, verbose=False)
        all_boxes = []

        for r in results:
            for box in r.boxes:
                all_boxes.append(box)

        # Phone Usage Detection
        is_phone_using = self.phone_detector.detect(all_boxes, model.names)

        if is_phone_using:
            cv2.putText(frame, "PHONE USAGE!", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        (0, 255, 255), 3)

        # Log phone event
        self.logger.handle_event("phone", is_phone_using)

        # Away-from-desk Detection
        person_present = any(
            model.names[int(box.cls[0])] == "person"
            for box in all_boxes
        )

        is_away = self.away_detector.update(person_present)

        if is_away:
            cv2.putText(frame, "AWAY FROM DESK!", (50, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        (255, 0, 0), 3)

        # Log away event
        self.logger.handle_event("away", is_away)

        # Draw YOLO bounding boxes
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[cls]

                color = (0, 255, 0)

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

        # Add status overlay
        status_text = f"Frame: {self.frame_count} | Sleep: {is_sleeping} | Phone: {is_phone_using} | Away: {is_away}"
        cv2.putText(frame, status_text, (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def run_loop(self):
        """Main detection loop (for windowed mode)"""
        while self.running:
            frame = self.process_frame()
            if frame is None:
                break

            cv2.imshow("Employee Monitoring - AI Engine", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.stop()

    def run_headless(self):
        """Run without display window (for server mode)"""
        if self.show_preview:
            # Show preview window even in headless mode
            self.run_loop()
        else:
            while self.running:
                frame = self.process_frame()
                if frame is None:
                    break
                time.sleep(0.033)  # ~30 FPS

    def stop(self):
        """Stop detection"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n✅ AI Engine stopped")


# Global detector instance
detector = DetectionRunner(show_preview=False)


def start_detection_headless(show_preview=False):
    """Start detection without GUI (for Flask integration)"""
    global detector
    detector = DetectionRunner(show_preview=show_preview)
    detector.start()
    thread = threading.Thread(target=detector.run_headless, daemon=True)
    thread.start()
    return thread


def start_detection_windowed():
    """Start detection with GUI window"""
    detector = DetectionRunner(show_preview=True)
    detector.start()
    detector.run_loop()


if __name__ == "__main__":
    print("\n⚠️  Running in standalone mode with GUI")
    print("   For Flask integration, use run_integrated.py instead\n")
    start_detection_windowed()