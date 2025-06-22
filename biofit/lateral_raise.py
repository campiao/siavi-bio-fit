import cv2
from ultralytics import YOLO
import numpy as np
from repository import get_data
from repository import update_player

pose_model = YOLO("yolov8s-pose.pt")

LEFT_SHOULDER_INDEX = 5
RIGHT_SHOULDER_INDEX = 6
LEFT_WRIST_INDEX = 9
RIGHT_WRIST_INDEX = 10

cap = cv2.VideoCapture(0)

lateral_raise_count = 0
raise_state = "down"  # could be "up" or "down"

def is_arm_up(wrist_y, shoulder_y, threshold=30):
    return wrist_y <= shoulder_y - threshold  # braço está acima do ombro

# Load current player ID
with open("current_player_id.txt", "r") as f:
    current_id = f.read().strip()

# Get all players
players = get_data()

# Find current player by ID
current_player = next((p for p in players if p.id == current_id), None)

# Calcula as reps necessárias com base no nível
required_reps = 5 * current_player.level

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    results = pose_model(frame, verbose=False, conf=0.5)

    for person in results:
        if not results or len(results[0].keypoints.data) == 0:
            continue  # ignora frame sem deteções

        keypoints_tensor = person.keypoints.data[0]

        # extrair coordenadas
        ls_x, ls_y, ls_conf = keypoints_tensor[LEFT_SHOULDER_INDEX].tolist()
        rs_x, rs_y, rs_conf = keypoints_tensor[RIGHT_SHOULDER_INDEX].tolist()
        lw_x, lw_y, lw_conf = keypoints_tensor[LEFT_WRIST_INDEX].tolist()
        rw_x, rw_y, rw_conf = keypoints_tensor[RIGHT_WRIST_INDEX].tolist()

        # verificar se todos os pontos são confiáveis
        if all(conf > 0.5 for conf in [ls_conf, rs_conf, lw_conf, rw_conf]):
            left_up = is_arm_up(lw_y, ls_y)
            right_up = is_arm_up(rw_y, rs_y)

            # Mostrar estado dos braços
            status = f"L:{'UP' if left_up else 'DOWN'} R:{'UP' if right_up else 'DOWN'}"
            cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if left_up and right_up and raise_state == "down":
                raise_state = "up"
            elif not left_up and not right_up and raise_state == "up":
                raise_state = "down"
                lateral_raise_count += 1
                print(f"Lateral Raise Count: {lateral_raise_count}")
            
            # repetições consoante o nível
            if lateral_raise_count >= required_reps:
                lateral_raise_count = 0
                current_player.level += 1
                print(f"LEVEL UP! New level: {current_player.level}")
                required_reps = 5 * current_player.level
                update_player(current_player)

        # Mostrar contagem no ecrã
        cv2.putText(
                frame,
                f"Reps: {lateral_raise_count}/{required_reps}  |  Level: {current_player.level}",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
        )

        annotated_frame = person.plot()
        cv2.imshow("Lateral Raise Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
