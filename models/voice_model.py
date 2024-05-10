from transformers import pipeline
from datasets import load_dataset
import soundfile as sf
import torch

class Voice:
    def __init__(self) -> None:
        self.synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")
        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)


    def construct_voice(self, response: str) -> str:
        file_name = 'response.wav'
        file_path = ''
        
        speech = self.synthesiser(response, forward_params={"speaker_embeddings": self.speaker_embedding})
        sf.write(file_path+file_name, speech["audio"], samplerate=speech["sampling_rate"])
        
        return file_path + file_name