from typing import NoReturn, Tuple
import os
import wave
import pyaudio

from models.brain_model import  Brain
from models.web_loader_model import  Web_Loader
from models.configurations import  Configurator
from models.memory_model import Memory
from models.voice_model import Voice
from models.recommendation_model import Recommendation

# instantiate class objects
voice: Voice = Voice()
config: Configurator = Configurator()
memory: Memory = Memory()
crawler: Web_Loader = Web_Loader(config=config)
brain: Brain = Brain(config=config, crawler=crawler, memory=memory)
recommendation: Recommendation = Recommendation(config=config, memory=memory)

def search(query: str) -> str:
    response = brain.in_scope_search(query)
    return response

def get_voice_response(response: str) -> str:
    return voice.construct_voice(response=response)

def get_recommendations(query: str) -> list[str]:
    recommendations = recommendation.get_recommendations(query)
    return recommendations

    # # Open the WAV file
    # wf = wave.open(os.getcwd() + '/' + file, 'rb')

    # # Instantiate PyAudio
    # p = pyaudio.PyAudio()

    # # Open a stream
    # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
    #                 channels=wf.getnchannels(),
    #                 rate=wf.getframerate(),
    #                 output=True)

    # # Read data
    # data = wf.readframes(1024)

    # # Play the sound
    # while data:
    #     stream.write(data)
    #     data = wf.readframes(1024)

    # # Close the stream and PyAudio
    # stream.close()
    # p.terminate()    

# def get_recommendations(query: str) -> str:
#     return brain.get_recommendations(question=query)

# if __name__ == '__main__':
#     while True:
#         brain.in_scope_search(str(input("\nWhat to search? ")))