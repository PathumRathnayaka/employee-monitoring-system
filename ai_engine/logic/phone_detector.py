class PhoneDetector:

    def detect(self, boxes, model_names):
        """
        Input:
            boxes: YOLO detected boxes
            model_names: YOLO class names
        Output:
            True → phone usage detected
            False → no usage
        """

        person_boxes = []
        phone_boxes = []

        # Separate person and phone boxes
        for box in boxes:
            cls = int(box.cls[0])
            label = model_names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "person":
                person_boxes.append((x1, y1, x2, y2))
            elif label == "cell phone":
                phone_boxes.append((x1, y1, x2, y2))

        # If no person or no phone → not using phone
        if not person_boxes or not phone_boxes:
            return False

        # Check if phone is within or near person bbox
        for px1, py1, px2, py2 in person_boxes:
            for fx1, fy1, fx2, fy2 in phone_boxes:

                # Check overlapping (IOU logic simplified)
                if fx1 > px1 - 50 and fy1 > py1 - 50 and fx2 < px2 + 50 and fy2 < py2 + 50:
                    return True  # phone inside person zone

        return False
