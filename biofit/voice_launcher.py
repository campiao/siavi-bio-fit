import threading
from voice_handler import start_voice_control

voice_thread = None
voice_thread_stop_flag = None

def start_voice(language="en"):
    global voice_thread, voice_thread_stop_flag
    voice_thread = None
    voice_thread_stop_flag = threading.Event()
    voice_thread_stop_flag.clear()
    model_path = f"./VoiceModels/vosk-model-{language}"
    voice_thread = threading.Thread(target=start_voice_control, args=(model_path, voice_thread_stop_flag))
    voice_thread.start()
    return voice_thread, voice_thread_stop_flag
