import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor

# ===== CONFIG =====
INPUT_FILE = r"C:\Users\jvish\Desktop\livo-ai\transcripts\What_is_Deep_Learning_Deep_Learning_Vs_Machine_Learning__Complete_Deep_Learning_Course_fHF22Wxuyw4.txt"
OUTPUT_FILE = INPUT_FILE.replace(".txt", "_English.txt")

MODEL_NAME = "ai4bharat/indictrans2-indic-en-dist-200M"
BATCH_SIZE = 8
SRC_LANG = "hin_Deva"
TGT_LANG = "eng_Latn"

device = "cuda" if torch.cuda.is_available() else "cpu"

# ===== LOAD MODEL =====
print("Loading IndicTrans2 model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, trust_remote_code=True).to(device)
processor = IndicProcessor(inference=True)

# ===== READ FILE =====
timestamps = []
texts = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        if line.startswith("[") and "]" in line:
            ts, text = line.split("]", 1)
            timestamps.append(ts + "]")
            texts.append(text.strip())
        else:
            timestamps.append("")
            texts.append(line)


# ===== TRANSLATION =====
def translate_batch(texts, batch_size=8):
    translated = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Preprocess batch with IndicProcessor
        batch = processor.preprocess_batch(
            batch,
            src_lang=SRC_LANG,
            tgt_lang=TGT_LANG,
        )

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(device)

        outputs = model.generate(
            **inputs,
            max_length=256
        )

        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # Postprocess translations
        decoded = processor.postprocess_batch(decoded, lang=TGT_LANG)

        translated.extend(decoded)

        print(f"Processed {min(i + batch_size, len(texts))}/{len(texts)}")

    return translated


print("Translating...")
translated_texts = translate_batch(texts, BATCH_SIZE)


# ===== SAVE =====
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ts, txt in zip(timestamps, translated_texts):
        if ts:
            f.write(f"{ts} {txt}\n")
        else:
            f.write(f"{txt}\n")

print(f"\nSaved to:\n{OUTPUT_FILE}")