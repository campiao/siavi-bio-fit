import threading
import cv2
import datetime
import face_recognition
import numpy as np
import repository as db
import time
from voice_launcher import start_voice
from command import get_command, clear
import subprocess
import sys
from current_player import set_player, clear_player

cap = cv2.VideoCapture(0)
window_name = "SIAVIBioFitG4"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
fonte = cv2.FONT_HERSHEY_SIMPLEX

players = db.get_data()
saved_encodings = db.extract_encodings(players)
player = None


boot = True
found = False
register = False

registerIndex = 0
name = None
gender = None
age = None

voice_thread, voice_thread_stop_flag = start_voice("en")


def run_app_menu():
    subprocess.Popen([sys.executable, "biofit/app_menu.py"])

# Libera a câmera e fecha a janela
def close_window():
    voice_thread_stop_flag.set()
    if voice_thread and voice_thread.is_alive():
        voice_thread.join(timeout=2)  
    cap.release()
    cv2.destroyAllWindows()

def define_encoding(frame_rgb) -> bool:
        global register, player, name, gender, age
        face_locations = face_recognition.face_locations(frame_rgb)

        if not face_locations:
            print("No face detected.")
            return False

        top, right, bottom, left = face_locations[0]
        centro_x = (left + right) // 2
        centro_y = (top + bottom) // 2

        if zona_esquerda < centro_x < zona_direita and zona_superior < centro_y < zona_inferior:
            encoding = face_recognition.face_encodings(frame_rgb, [face_locations[0]])[0]
            player = db.Player(name=name,
                    age=age,
                    gender=gender,
                    face_encoding=encoding.tolist())
            db.register(player)
            set_player(player)
            print("Face centralized. Encoding generated with success!")
            register = False
            return True
        else:
            print("Face detected, not centred.")


initial_time = time.time()
ultimo_tempo = 0  # Marca do último momento em que executou
intervalo = 2 
title = "SIAVIBioFIT"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    photo_frame = frame.copy()
    altura, largura, _ = frame.shape
    hora = datetime.datetime.now().strftime("%H:%M")
    cv2.putText(frame, hora, (largura - 100, altura - 5), fonte, 1, (255, 255, 255), 2)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    (tw, th), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 2, 4)
    x = (largura - tw) // 2
    y = th + 10
    cv2.putText(frame, title,(x, y), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 8)  # border
    cv2.putText(frame, title,(x,y), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 4)

    if not found and not register:
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
                        set_player(player)
                        player = players[idx]
                        nome = player.name
                        found = True
                        register = False
                        with open("current_player_id.txt", "w") as f:
                            f.write(player.id)
                ultimo_tempo = agora

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, nome, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        if time.time() - initial_time > 2:
            (tw, th), _ = cv2.getTextSize("USER NOT FOUND! REGISTER?", fonte, 0.9, 2)
            x = (largura - tw) // 2
            y = th + int(altura * 0.80)
            cv2.putText(frame, "USER NOT FOUND! REGISTER?", (x, y), fonte, 0.9, (0, 255, 0), 2)

    if register:
        # Desenhar zona central de validação (ex: área de 40% central da tela)
        zona_esquerda = int(largura * 0.35)
        zona_direita = int(largura * 0.65)
        zona_superior = int(altura * 0.3)
        zona_inferior = int(altura * 0.7)

       
        cv2.rectangle(frame, (zona_esquerda, zona_superior), (zona_direita, zona_inferior), (255, 255, 0), 2)

        if get_command() == "name":
            clear()
            registerIndex = 0
        if get_command() == "gender":
            clear()
            registerIndex = 1
        if get_command() == "age":
            clear()
            registerIndex = 2
        if get_command() == "save":
            registerIndex = -1

        if registerIndex == 0:
            name = get_command().capitalize()
            cv2.putText(frame,"Name: " + name,( int(0.01*largura) , int(0.45*altura)),fonte,0.6, (150, 200, 0), 2)
        else:
            cv2.putText(frame,"Name: " + (name if name else ""),( int(0.01*largura) , int(0.45*altura)),fonte,0.6, (255, 255, 0), 2)

        if registerIndex == 1:
            gender = get_command().capitalize()
            cv2.putText(frame,"Gender: " + gender,( int(0.01*largura) , int(0.50*altura)),fonte,0.6, (150, 200, 0), 2)
        else:
            cv2.putText(frame,"Gender: " + (gender if gender else ""),( int(0.01*largura) , int(0.50*altura)),fonte,0.6, (255, 255, 0), 2)
    
        if registerIndex == 2:
            age = str(get_command())
            cv2.putText(frame,"Age: " + age,( int(0.01*largura) , int(0.55*altura)),fonte,0.6, (150, 200, 0), 2)
        else:
            cv2.putText(frame,"Age: " + (age if age else ""),( int(0.01*largura) , int(0.55*altura)),fonte,0.6, (255, 255, 0), 2)

        if name and age and gender:
            cv2.putText(frame,"Center face on square and",( int(0.20*largura) , int(0.8*altura)),fonte,0.9, (255, 255, 0), 2)
            cv2.putText(frame,"Say 'Save' to complete",( int(0.25*largura) , int(0.85*altura)),fonte,0.9, (255, 255, 0), 2)
            if get_command() == "save":
                found = define_encoding(frame_rgb)

    if player and not register and found:
        
        text1 = "Face Detected"
        text2 = "Welcome " + player.name + "!"

        if time.time() - ultimo_tempo < 3:
            (tw, th), _ = cv2.getTextSize(text1, fonte, 1, 2)
            x = (largura - tw) // 2
            y = th + int(altura * 0.70)
            cv2.putText(frame, text1, (x, y), fonte, 1, (0, 0, 0), 4)
            cv2.putText(frame, text1, (x, y), fonte, 1, (255, 255, 0), 2)

        (tw, th), _ = cv2.getTextSize(text2, fonte, 1, 2)
        x = (largura - tw) // 2
        y = th + int(altura * 0.78)
        cv2.putText(frame, text2, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        cv2.putText(frame, text2, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        if get_command() == "log out":
            clear()
            clear_player()
            player = None
            found = False
            register = False

        if time.time() - ultimo_tempo > 5:
            text3 = "REDIRECTING TO EXERCISES"
            (tw, th), _ = cv2.getTextSize(text3, fonte, 0.9, 2)
            x = (largura - tw) // 2
            y = th + int(altura * 0.93)
            cv2.putText(frame, text3, (x, y), fonte, 0.9, (0, 255, 0), 2)
            
        if time.time() - ultimo_tempo > 7:
            run_app_menu()
            close_window()
            break

    cv2.imshow(window_name, frame)

    if not register and not found:
        if get_command() == 'register':
            register = True
            clear()
    
    if get_command() == "exit":
        break

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('f'): 
        if not found:
            found = define_encoding(frame_rgb)
    elif key == ord('r'):
        if not register and not found:
            register = True
            
close_window()
