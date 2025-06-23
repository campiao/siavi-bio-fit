import time
import threading
import customtkinter
from command import get_command
from voice_launcher import start_voice
from repository import get_data
import current_player as cp
import bicep_curl
import lateral_raise
import jumping_jacks

app = customtkinter.CTk()

info_label = None
labels = []

# === Start voice recognition ===
voice_thread, voice_thread_stop_flag = start_voice("en")

# === Voice command loop ===
def voice_command_loop():
    while not voice_thread_stop_flag.is_set():
        command = get_command()
        if command:
            command = command.lower()
            if "bicep" in command:
                info_label.configure(text="Starting bicep curl exercise.")
                run_bicepcurl()
                end_level()
            elif "jumping jacks" in command:
                info_label.configure(text="Starting jumping jacks exercise.")
                run_jumpingjacks()
                end_level()
            elif "lateral raise" in command:
                info_label.configure(text="Starting lateral raise exercise.")
                run_lateralraise()
                end_level()
            elif "exit" in command:
                info_label.configure(text="Exiting...")
                on_closing()
                break
        
        time.sleep(0.1)

voice_loop_thread = threading.Thread(target=voice_command_loop, daemon=True)
voice_loop_thread.start()

# === Close Handler ===
def on_closing():
    voice_thread_stop_flag.set()      # Signal the thread to stop
    if voice_thread and voice_thread.is_alive():
        voice_thread.join(timeout=2)  # define timeout!
    print("Shutting down voice recognition...")
    app.destroy()


# === Exercise commands ===
def run_bicepcurl():
    bicep_curl.do_bicep()

def run_jumpingjacks():
   jumping_jacks.do_jumping_jacks()

def run_lateralraise():
    lateral_raise.do_lateral_raises()

# Load current player ID
with open("current_player_id.txt", "r") as f:
    current_id = f.read().strip()

# Get all players
players = get_data()

# Find current player by ID
current_player = next((p for p in players if p.id == current_id), None)
cp.set_player(current_player)
data = [f"Name: {current_player.name}", f"Age: {current_player.age}", f"Gender: {current_player.gender}", f"Level: {current_player.level}"]

# === GUI Setup ===
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
app.geometry("300x480")
app.protocol("WM_DELETE_WINDOW", on_closing)

info_frame = customtkinter.CTkFrame(app)
info_frame.pack(pady=10)


for i, txt in enumerate(data):
    label = customtkinter.CTkLabel(info_frame, text=txt)
    label.grid(row=0, column=i, padx=5)

title = customtkinter.CTkLabel(app, text="Exercises")
title.pack(padx=20, pady=20)

jjBTN = customtkinter.CTkButton(app, text="Jumping Jacks", command=run_jumpingjacks)
jjBTN.pack(padx=20, pady=20)

bcBTN = customtkinter.CTkButton(app, text="Bicep Curls", command=run_bicepcurl)
bcBTN.pack(padx=20, pady=20)

lrBTN = customtkinter.CTkButton(app, text="Lateral Raise", command=run_lateralraise)
lrBTN.pack(padx=20, pady=20)

info_label = customtkinter.CTkLabel(app, text="")
info_label.pack(pady=20)


def update_labels(nova_data):
    for i, txt in enumerate(nova_data):
        if i < len(labels):
            labels[i].configure(text=txt)
        else:
            # Se houver mais dados que labels, cria novos
            label = customtkinter.CTkLabel(info_frame, text=txt)
            label.grid(row=0, column=i, padx=5)
            labels.append(label)

def end_level():
    info_label.configure(text="")
    current_player = cp.get_player()
    data = [f"Name: {current_player.name}", f"Age: {current_player.age}", f"Gender: {current_player.gender}", f"Level: {current_player.level}"]
    update_labels(data)

# === Run the GUI ===
app.mainloop()
