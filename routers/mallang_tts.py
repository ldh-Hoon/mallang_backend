import os
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from huggingface_hub import snapshot_download

if not os.path.isdir("model"):
    snapshot_download(repo_id="princesslucy/mallang_xtts_v2", local_dir='./model')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
config = XttsConfig()
config.load_json("./model/config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="./model")
model.to(device)

def tts(text, speed, audio, output, temperature=0.8, length_penalty=0.1, repetition_penalty=2.0):
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=[audio])

    out = model.inference(
    text,
    gpt_cond_latent=gpt_cond_latent,
    speaker_embedding=speaker_embedding,
    temperature=temperature, # Add custom parameters here
    language="ko",
    length_penalty=length_penalty,
    repetition_penalty=repetition_penalty,
    speed=speed,
    enable_text_splitting=False,
    )

    return torchaudio.save(output, torch.tensor(out["wav"]).unsqueeze(0), 24000)