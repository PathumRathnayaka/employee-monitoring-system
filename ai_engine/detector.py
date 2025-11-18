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
    def __init__(self, show_preview=True):
        self.running = False
        self.cap = None
        self.show_preview = show_preview
        self.frame_count = 0
        self.current_alerts = []

        # Accuracy improvements - slower but more accurate
        self.detection_interval = 3  # Process every 3 frames (was every frame)
        self.confirmation_frames = 5  # Need 5 consecutive detections to confirm
        self.sleep_buffer = []
        self.phone_buffer = []
        self.away_buffer = []

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

        # Set camera properties for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Initialize detectors
        self.sleep_detector = SleepDetector()
        self.sleep_detector.setup()
        self.sleep_pose_detector = SleepPoseDetector()
        self.phone_detector = PhoneDetector()
        self.away_detector = AwayDetector()

        # Event logger (removed socket emissions for accuracy)
        self.logger = EventLogger(employee_id="001")

        print("=" * 60)
        print("🔵 AI Engine Started (Accuracy Mode)")
        print("📹 Webcam: Active")
        print("🎯 Mode: High Accuracy (Slower but more reliable)")
        print("=" * 60)

    def confirm_detection(self, buffer, current_state):
        """Confirm detection only after multiple consecutive frames"""
        buffer.append(current_state)

        # Keep buffer size manageable
        if len(buffer) > self.confirmation_frames:
            buffer.pop(0)

        # Need majority of frames to confirm
        if len(buffer) >= self.confirmation_frames:
            true_count = sum(buffer)
            return true_count >= (self.confirmation_frames * 0.6)  # 60% threshold

        return False

    def process_frame(self):
        """Process a single frame with accuracy focus"""
        if not self.running or not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        self.frame_count += 1
        self.current_alerts = []

        # Only process detection every N frames for accuracy
        should_detect = (self.frame_count % self.detection_interval == 0)

        if should_detect:
            # Sleep Detection - with confirmation
            is_sleeping_eye = self.sleep_detector.detect(frame)
            is_sleeping_pose = self.sleep_pose_detector.detect(frame)
            is_sleeping_raw = is_sleeping_eye or is_sleeping_pose

            is_sleeping = self.confirm_detection(self.sleep_buffer, is_sleeping_raw)

            if is_sleeping:
                self.current_alerts.append("SLEEPING")
                self.logger.handle_event("sleep", True)
            elif len(self.sleep_buffer) >= self.confirmation_frames and not is_sleeping:
                self.logger.handle_event("sleep", False)

            # YOLO Object Detection - run on every detection frame
            results = model(frame, verbose=False, conf=0.5)  # Increased confidence threshold
            all_boxes = []

            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        all_boxes.append(box)

            # Phone Usage Detection - with confirmation
            is_phone_using_raw = self.phone_detector.detect(all_boxes, model.names)
            is_phone_using = self.confirm_detection(self.phone_buffer, is_phone_using_raw)

            if is_phone_using:
                self.current_alerts.append("PHONE USAGE")
                self.logger.handle_event("phone", True)
            elif len(self.phone_buffer) >= self.confirmation_frames and not is_phone_using:
                self.logger.handle_event("phone", False)

            # Away-from-desk Detection - with confirmation
            person_present = any(
                model.names[int(box.cls[0])] == "person"
                for box in all_boxes
            )

            is_away_raw = self.away_detector.update(person_present)
            is_away = self.confirm_detection(self.away_buffer, is_away_raw)

            if is_away:
                self.current_alerts.append("AWAY FROM DESK")
                self.logger.handle_event("away", True)
            elif len(self.away_buffer) >= self.confirmation_frames and not is_away:
                self.logger.handle_event("away", False)

            # Draw ALL bounding boxes with labels
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        # Get box data
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        label = model.names[cls]

                        # Color coding
                        color = (0, 255, 0)  # Green default
                        thickness = 2

                        # Special highlighting
                        if label == "cell phone":
                            if is_phone_using:
                                color = (0, 255, 255)  # Yellow for active phone
                                thickness = 4
                            else:
                                color = (255, 0, 255)  # Magenta for detected phone
                                thickness = 3
                        elif label == "person":
                            color = (0, 255, 0)  # Green for person
                            thickness = 3

                        # Draw rectangle - ALWAYS draw boxes
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

                        # Draw label with background
                        label_text = f"{label} {conf:.2f}"
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.7
                        font_thickness = 2

                        (text_width, text_height), baseline = cv2.getTextSize(
                            label_text, font, font_scale, font_thickness
                        )

                        # Draw filled rectangle behind text
                        cv2.rectangle(
                            frame,
                            (x1, y1 - text_height - baseline - 8),
                            (x1 + text_width + 10, y1),
                            color,
                            -1
                        )

                        # Draw label text in black
                        cv2.putText(
                            frame,
                            label_text,
                            (x1 + 5, y1 - baseline - 5),
                            font,
                            font_scale,
                            (0, 0, 0),
                            font_thickness
                        )

        # Always draw current alerts (even on non-detection frames)
        alert_y = 40
        for alert in self.current_alerts:
            if alert == "SLEEPING":
                color = (0, 0, 255)  # Red
                icon = "😴"
            elif alert == "PHONE USAGE":
                color = (0, 255, 255)  # Yellow
                icon = "📱"
            elif alert == "AWAY FROM DESK":
                color = (255, 0, 0)  # Blue
                icon = "🚶"
            else:
                color = (255, 255, 255)
                icon = "⚠️"

            alert_text = f"{icon} {alert} {icon}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            font_thickness = 3

            (text_w, text_h), baseline = cv2.getTextSize(
                alert_text, font, font_scale, font_thickness
            )

            # Draw background
            cv2.rectangle(
                frame,
                (10, alert_y - text_h - 10),
                (text_w + 30, alert_y + 10),
                color,
                -1
            )

            # Draw border
            cv2.rectangle(
                frame,
                (10, alert_y - text_h - 10),
                (text_w + 30, alert_y + 10),
                (0, 0, 0),
                2
            )

            # Draw text
            cv2.putText(
                frame,
                alert_text,
                (20, alert_y),
                font,
                font_scale,
                (255, 255, 255),
                font_thickness
            )

            alert_y += text_h + 40

        # Status bar
        status_bar_height = 50
        cv2.rectangle(
            frame,
            (0, frame.shape[0] - status_bar_height),
            (frame.shape[1], frame.shape[0]),
            (0, 0, 0),
            -1
        )

        # Get detection info
        if should_detect and 'all_boxes' in locals():
            detected_count = len(all_boxes)
            person_status = "✓" if person_present else "✗"
        else:
            detected_count = 0
            person_status = "..."

        status_text = f"Frame: {self.frame_count} | Objects: {detected_count} | Person: {person_status}"
        status_text += f" | Mode: High Accuracy"

        cv2.putText(
            frame,
            status_text,
            (10, frame.shape[0] - 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        return frame

    def run_loop(self):
        """Main detection loop - runs in main thread"""
        print("🎥 Opening camera window...")

        while self.running:
            frame = self.process_frame()
            if frame is None:
                print("⚠️ Failed to read frame from camera")
                break

            # Display the frame
            cv2.imshow("Employee Monitoring - High Accuracy Mode", frame)

            # Check for 'q' key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 User pressed 'q' - closing camera window")
                break

        self.stop()

    def run_headless(self):
        """Run without display window"""
        while self.running:
            frame = self.process_frame()
            if frame is None:
                break
            time.sleep(0.033)  # ~30 FPS

    def stop(self):
        """Stop detection and cleanup"""
        print("\n🛑 Stopping AI Engine...")
        self.running = False
        if self.cap:
            self.cap.release()
            print("📹 Camera released")
        cv2.destroyAllWindows()
        print("✅ AI Engine stopped\n")


# Global detector instance
detector = DetectionRunner(show_preview=True)


def start_detection_headless(show_preview=True):
    """Start detection with optional preview"""
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