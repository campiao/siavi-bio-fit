import cv2
from ultralytics import YOLO
import numpy as np
from repository import get_data, update_player
from command import get_command, clear
import current_player as cp

# Load Pose Model
pose_model = YOLO("yolov8s-pose.pt")

def calculate_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def do_jumping_jacks(): 
    global pose_model
    # Keypoint indices
    LEFT_WRIST = 9
    RIGHT_WRIST = 10
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16

    # Camera input
    cap = cv2.VideoCapture(0)

    jj_count = 0
    state = "closed"  # Initial state: arms down, legs together


    current_player = cp.get_player()
    required_reps = 5 * current_player.level

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = pose_model(frame, verbose=False, conf=0.5)

        for person in results:
            if not results or len(results[0].keypoints.data) == 0:
                continue
            
            keypoints = person.keypoints.data[0]

            lw_x, lw_y, conf_lw = keypoints[LEFT_WRIST].tolist()
            rw_x, rw_y, conf_rw = keypoints[RIGHT_WRIST].tolist()
            la_x, la_y, conf_la = keypoints[LEFT_ANKLE].tolist()
            ra_x, ra_y, conf_ra = keypoints[RIGHT_ANKLE].tolist()

            if min(conf_lw, conf_rw, conf_la, conf_ra) >= 0.5:
                ankle_dist = calculate_distance((la_x, la_y), (ra_x, ra_y))
                wrist_avg_y = (lw_y + rw_y) / 2
                #ankle_dist = 100

                # Thresholds (empirical, may need tuning)
                legs_apart = ankle_dist > 150
                arms_up = wrist_avg_y < keypoints[0][1]  # Y of nose

                if state == "closed" and legs_apart and arms_up:
                    state = "open"
                elif state == "open" and not legs_apart and not arms_up:
                    jj_count += 1
                    state = "closed"
                    print(f"Jumping Jack Count: {jj_count}")

                    if jj_count >= required_reps:
                        jj_count = 0
                        current_player.level += 1
                        print(f"LEVEL UP! New level: {current_player.level}")
                        required_reps = 5 * current_player.level
                        update_player(current_player)

        # Overlay info
        cv2.putText(frame, f"Reps: {jj_count}/{required_reps} | Level: {current_player.level}", (50, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2)

        # Draw name
        annotated = person.plot()
        for box in person.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.putText(annotated, current_player.name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imshow("Jumping Jacks Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            cp.set_player(current_player)
            break

        if get_command() == "exit":
            cp.set_player(current_player)
            clear()
            break

    cap.release()
    cv2.destroyAllWindows()
