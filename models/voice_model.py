# from transformers import pipeline
# from datasets import load_dataset
# import torch
# from parler_tts import ParlerTTSForConditionalGeneration
# from transformers import AutoTokenizer
# import soundfile as sf
# from pathlib import Path
from openai import OpenAI

class Voice:
    def __init__(self) -> None:
        # self.synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")
        # embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        # self.speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

        # self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        # self.model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler_tts_mini_v0.1").to(self.device)
        # self.tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler_tts_mini_v0.1")
        
        # description = "A female speaker with a slightly low-pitched voice delivers her words quite expressively, in a very confined sounding environment with clear audio quality. She speaks very fast."

        # self.input_ids = self.tokenizer(description, return_tensors="pt").input_ids.to(self.device)
        pass

    @DeprecationWarning
    def construct_voice(self, response: str) -> str:
        file_name = 'response.wav'
        file_path = ''
        
        speech = self.synthesiser(response, forward_params={"speaker_embeddings": self.speaker_embedding})
        sf.write(file_path+file_name, speech["audio"], samplerate=speech["sampling_rate"])
        
        return file_path + file_name
    
    @DeprecationWarning
    def mello(self, response: str) -> str:
        file_name = 'response.wav'
        file_path = ''
        
        prompt_input_ids = self.tokenizer(response, return_tensors="pt").input_ids.to(self.device)
        generation = self.model.generate(input_ids=self.input_ids, prompt_input_ids=prompt_input_ids)
        audio_arr = generation.cpu().numpy().squeeze()
        
        sf.write(file_path+file_name, audio_arr, self.model.config.sampling_rate)
        
        return file_path + file_name
    
    def open_ai(self, response: str) -> str:
        file_name = 'response.wav'
        file_path = ''
        
        client = OpenAI()
        speech_file_path = file_path + file_name
        response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=response
        )

        response.stream_to_file(speech_file_path)
        
        return file_path + file_name
