import cv2
from ultralytics import YOLO
import numpy as np

# Load Model
pose_model = YOLO("yolov8s-pose.pt")

# Keypoint names
keypoint_names = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]

# defining keypoint indices for left arm
LEFT_SHOULDER_INDEX = 5
LEFT_ELBOW_INDEX = 7
LEFT_WRIST_INDEX = 9


# Open the webcam
cap = cv2.VideoCapture(0)

# initialization of curl tracking variables
bicep_curl_count = 0
curl_position_state = None  # can be "down" or "up"

def calculate_joint_angle(point_a, point_b, point_c):
    """
    Calculates the angle (in degrees) between three points at point_b.
    Used to compute the elbow angle for a bicep curl.
    """
    point_a = np.array(point_a)
    point_b = np.array(point_b)
    point_c = np.array(point_c)

    # vectors from b to a and b to c
    vector_ba = point_a - point_b
    vector_bc = point_c - point_b

    # Compute angle using dot product
    cosine_angle = np.dot(vector_ba, vector_bc) / (np.linalg.norm(vector_ba) * np.linalg.norm(vector_bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)

while cap.isOpened():
    success, frame = cap.read()

    if not success:
        break

    # Run pose detection
    results = pose_model(frame, verbose=False, conf=0.5)

    for person in results:
        keypoints_tensor = person.keypoints.data[0]  # Shape: (17, 3)

        # Extract relevant keypoints and their confidences
        left_shoulder = keypoints_tensor[LEFT_SHOULDER_INDEX]
        left_elbow = keypoints_tensor[LEFT_ELBOW_INDEX]
        left_wrist = keypoints_tensor[LEFT_WRIST_INDEX]

        shoulder_x, shoulder_y, conf_shoulder = left_shoulder.tolist()
        elbow_x, elbow_y, conf_elbow = left_elbow.tolist()
        wrist_x, wrist_y, conf_wrist = left_wrist.tolist()

        # Check confidence threshold
        if conf_shoulder > 0.5 and conf_elbow > 0.5 and conf_wrist > 0.5:
            # Calculate elbow angle
            elbow_angle = calculate_joint_angle(
                (shoulder_x, shoulder_y),
                (elbow_x, elbow_y),
                (wrist_x, wrist_y)
            )

            # Show angle on screen
            cv2.putText(frame, f"Elbow Angle: {int(elbow_angle)}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Count curls
            if elbow_angle > 160:
                curl_position_state = "down"
            elif elbow_angle < 40 and curl_position_state == "down":
                curl_position_state = "up"
                bicep_curl_count += 1
                print(f"Bicep Curl Count: {bicep_curl_count}")
        else:
            print("Low confidence keypoints – skipping this frame.")
            
        cv2.putText(
            frame,
            f"Curl Count: {bicep_curl_count}",
            (50, 100),  # Position on screen (x, y)
            cv2.FONT_HERSHEY_SIMPLEX,
            1,          # Font scale
            (255, 0, 0),  # Color (Blue in BGR)
            2           # Thickness
        )

        # Show frame with pose overlay
        annotated_frame = person.plot()
        cv2.imshow("Pose Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()