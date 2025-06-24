from face_recon_register import run_face_recognition
import voice_launcher


def main():
    voice_launcher.start_voice("en")
    run_face_recognition(voice_launcher.voice_thread,
                         voice_launcher.voice_thread_stop_flag,
                         )

main()
