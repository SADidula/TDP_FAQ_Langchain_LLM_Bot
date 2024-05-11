from typing import NoReturn, Tuple
import os
import wave
# import pyaudio

from models.brain_model import  Brain
from models.web_loader_model import  Web_Loader
from models.configurations import  Configurator
from models.voice_model import Voice

# instantiate class objects
voice: Voice = Voice()
config: Configurator = Configurator()
crawler: Web_Loader = Web_Loader(config=config)
brain: Brain = Brain(config=config, crawler=crawler)

def search(query: str) -> str:
    return brain.in_scope_search(query)

def get_voice_response(response: str) -> str:
    return voice.open_ai(response=response)

def get_recommendations(query: str) -> list[str]:
    return brain.predict_questions(question=query)

@DeprecationWarning
def play_voice_on_req(response: str):
    file = voice.construct_voice(response=response)
    # Open the WAV file
    wf = wave.open(os.getcwd() + '/' + file, 'rb')

    # Instantiate PyAudio
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data
    data = wf.readframes(1024)

    # Play the sound
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Close the stream and PyAudio
    stream.close()
    p.terminate()    

# def get_recommendations(query: str) -> str:
#     return brain.get_recommendations(question=query)

# if __name__ == '__main__':
#     while True:
#         brain.in_scope_search(str(input("\nWhat to search? ")))