import cv2
import datetime
import face_recognition
import numpy as np
import repository as db
import time

cap = cv2.VideoCapture(0)
foto_count = 0

window_name = "SIAVIBioFitG4"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
fonte = cv2.FONT_HERSHEY_SIMPLEX

players = db.get_data()
saved_encodings = db.extract_encodings(players)
player = None

boot = True
found = False
register = False

def define_encoding(frame_rgb) -> bool:
        global register
        face_locations = face_recognition.face_locations(frame_rgb)

        if not face_locations:
            print("No face detected.")
            return False

        top, right, bottom, left = face_locations[0]
        centro_x = (left + right) // 2
        centro_y = (top + bottom) // 2

        if zona_esquerda < centro_x < zona_direita and zona_superior < centro_y < zona_inferior:
            encoding = face_recognition.face_encodings(frame_rgb, [face_locations[0]])[0]
            db.register(db.Player(name="Rui",
                    age=23,
                    gender="M",
                    face_encoding=encoding.tolist())
                    )
            print("Face centralized. Encoding generated with success!")
            register = False
            return True
        else:
            print("Face detected, not centred.")


ultimo_tempo = 0  # Marca do último momento em que executou
intervalo = 2 

while True:
    ret, frame = cap.read()
    if not ret:
        break

    photo_frame = frame.copy()
    altura, largura, _ = frame.shape
    hora = datetime.datetime.now().strftime("%H:%M")
    cv2.putText(frame, hora, (largura - 100, altura - 5), fonte, 1, (255, 255, 255), 2)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    if not found and not register:
        (tw, th), _ = cv2.getTextSize("USER NOT FOUND!REGISTER?(r)",  cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        x = (largura - tw) // 2
        y = th + 10 
        cv2.putText(frame, "USER NOT FOUND!REGISTER?(r)", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        small_frame = cv2.resize(frame_rgb, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small_frame)
        nome = "Unknown"
        if face_locations:
            top, right, bottom, left = face_locations[0]
            agora = time.time()
            if agora - ultimo_tempo >= intervalo:
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(saved_encodings, face_encoding, tolerance=0.6)
                    nome = "Unknown"
       
                    if True in matches:
                        face_distances = face_recognition.face_distance(saved_encodings, face_encoding)
                        idx = np.argmin(face_distances)
                        player = players[idx]
                        nome = player.name
                        found = True
                        register = False
                ultimo_tempo = agora

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, nome, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        

    if register:
        # Desenhar zona central de validação (ex: área de 40% central da tela)
        zona_esquerda = int(largura * 0.35)
        zona_direita = int(largura * 0.65)
        zona_superior = int(altura * 0.3)
        zona_inferior = int(altura * 0.7)

        # Desenha um retângulo visual da zona central
        cv2.rectangle(frame, (zona_esquerda, zona_superior), (zona_direita, zona_inferior), (255, 255, 0), 2)

    if player and not register and found:
        cv2.putText(frame, "WELCOME " + player.name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

    cv2.imshow(window_name, frame)


    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('f'):  # Tecla 'f' → tirar foto
        if not found:
            found = define_encoding(frame_rgb)
    elif key == ord('r'):
        if not register:
            register = True
            

# Libera a câmera e fecha a janela
cap.release()
cv2.destroyAllWindows()
