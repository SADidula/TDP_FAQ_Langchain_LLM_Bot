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
