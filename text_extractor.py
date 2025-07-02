import shutil
import time
from pathlib import Path
from PIL import Image
import google.generativeai as genai
from spire.presentation import Presentation
import streamlit as st
from utlis.logger import Logger

# Add custom fonts folder
Presentation().SetCustomFontsFolder("./app/fonts")


def initialize(goole_api_key):
    genai.configure(api_key=goole_api_key)
    vision_model = genai.GenerativeModel(st.secrets['GEMINI_MODEL_ID'])
    return vision_model


def save_file(uploaded_file,save_folder_path):
    save_path = Path(save_folder_path, uploaded_file.name)
    with open(save_path, mode='wb') as w:
        w.write(uploaded_file.read())

    Logger().info(f'[INFO] File saved to {save_path}')
    return str(save_path)


def ppt_to_img(filepath,save_image_path):
    presentation = Presentation()
    presentation.LoadFromFile(filepath)

    save_folder = f'{save_image_path}{filepath}'
    save_path = Path(save_folder)

    if save_path.exists():
        shutil.rmtree(save_path, ignore_errors=True)
    save_path.mkdir(parents=True, exist_ok=True)

    for i, slide in enumerate(presentation.Slides):
        if i < 10:
            filename = save_path / f"ToImage_{i+1}.png"
            image = slide.SaveAsImage()
            image.Save(str(filename))
            image.Dispose()

    ppt_len = presentation.Slides.Length
    presentation.Dispose()

    # print(f"[INFO] PPT converted to {ppt_len} images.")
    return ppt_len if ppt_len <= 10 else 10


def generate_summary(model, ppt_len, path_prefix):
    combine_text = {}
    for i in range(ppt_len):
        image_path = f"{path_prefix}{i+1}.png"
        image = Image.open(image_path)

        prompt = (
            st.secrets['OCR_PROMPT']
        )

        Logger().info(f"\n--- Slide {i+1} Summary ---")
        
        response = model.generate_content([prompt, image])
        combine_text[f"Slide {i+1}"]=response.text
        time.sleep(5)  # Respect rate limits
    return combine_text

