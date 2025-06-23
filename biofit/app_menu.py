import tkinter
import os
import threading
import customtkinter
import subprocess
import sys
import cv2
from command import get_command
from voice_launcher import start_voice
from repository import get_data, Player


# === Start voice recognition ===
voice_thread, voice_thread_stop_flag = start_voice("en")

# === Voice command loop ===
def voice_command_loop():
    while not voice_thread_stop_flag.is_set():
        command = get_command()
        if command:
            command = command.lower()
            if "bicep" in command:
                print("Starting bicep curl exercise.")
                run_bicepcurl()
            elif "jumping jacks" in command:
                print("Starting jumping jacks exercise.")
                run_jumpingjacks()
            elif "lateral raise" in command:
                print("Starting lateral raise exercise.")
                run_lateralraise()
            elif "exit" in command:
                on_closing()
                print("Exiting...")

# === Close Handler ===
def on_closing():
    voice_thread_stop_flag.set()      # Signal the thread to stop
    if voice_thread and voice_thread.is_alive():
        voice_thread.join(timeout=2)  # define timeout!
    print("Shutting down voice recognition...")
    app.destroy()
    


# === Exercise commands ===
def run_bicepcurl():
    script_path = os.path.join("biofit", "bicep_curl.py")
    subprocess.run([sys.executable, script_path])

def run_jumpingjacks():
    script_path = os.path.join("biofit", "jumping_jacks.py")
    subprocess.run([sys.executable, script_path])

def run_lateralraise():
    script_path = os.path.join("biofit", "lateral_raise.py")
    subprocess.run([sys.executable, script_path])

# Load current player ID
with open("current_player_id.txt", "r") as f:
    current_id = f.read().strip()

# Get all players
players = get_data()

# Find current player by ID
current_player = next((p for p in players if p.id == current_id), None)
data = [f"Name: {current_player.name}", f"Age: {current_player.age}", f"Gender: {current_player.gender}", f"Level: {current_player.level}"]

# === GUI Setup ===
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
app = customtkinter.CTk()
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

# === Run the GUI ===
app.mainloop()
