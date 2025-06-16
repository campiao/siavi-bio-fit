import tkinter
import customtkinter
import subprocess
import sys

def run_app_menu():
    subprocess.run([sys.executable, "app_menu.py"])
    
# appearence
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# app frame
app = customtkinter.CTk()
app.geometry("720x480")

title = customtkinter.CTkLabel(app, text="Main Menu")
title.pack(padx=20, pady=20)

registerBTN = customtkinter.CTkButton(app, text="Register")
registerBTN.pack(padx=20, pady=20)

enterBTN = customtkinter.CTkButton(app, text="Enter", command=run_app_menu)
enterBTN.pack(padx=20, pady=20)

# run window
app.mainloop()