from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
from text2digits.text2digits import Text2Digits
from command import set_command
from number_parser import parse_number


t2d = Text2Digits()
q = queue.Queue()


def start_voice_control(model_path, stop_flag):
    listen_voice(model_path, stop_flag)

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen_voice(model_path, stop_flag):
    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Listening model:", model_path)
        while not stop_flag.is_set():
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'text' in result and result['text']:
                    print(result['text'])
                    # Dividir o texto em palavras
                    words = result['text'].split()

                    # Verificar se o número de palavras é maior que 3
                    if len(words) <= 3:
                        converted = parse_number(result['text'])
                        if converted is not None:
                            set_command(converted)
                        else:
                            set_command(result['text'])
                    else:
                        print("Ignorando comando, mais de 3 palavras detectadas:", result['text'])