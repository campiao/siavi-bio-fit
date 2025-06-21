import tkinter
import customtkinter
import subprocess
import sys

# functions
def run_bicepcurl():
    subprocess.run([sys.executable, "bicep_curl.py"])

# appearence
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# app frame
app = customtkinter.CTk()
app.geometry("720x480")

title = customtkinter.CTkLabel(app, text="Exercises")
title.pack(padx=20, pady=20)

jjBTN = customtkinter.CTkButton(app, text="Jumping Jacks")
jjBTN.pack(padx=20, pady=20)

bcBTN = customtkinter.CTkButton(app, text="Bicep Curls", command=run_bicepcurl)
bcBTN.pack(padx=20, pady=20)

lrBTN = customtkinter.CTkButton(app, text="Lateral Raise")
lrBTN.pack(padx=20, pady=20)

# run window
app.mainloop()