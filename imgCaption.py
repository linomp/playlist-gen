import json
import os
import io
from dotenv import load_dotenv
import base64
import traceback
import numpy as np
from PIL import Image
from openai import OpenAI

from models import ImageCaption

"""
Image captioning with GPT-4
based on: https://github.com/42lux/CaptainCaption
"""
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


def generate_caption(image: np.ndarray, format:str, weather_desc:str) -> ImageCaption:
    first_part = f"The image contains a person and the current weather is {weather_desc}."
    prompt = first_part + """Based on their outfit and the vibe they give off, suggest at least two music genres they are most likely to enjoy given the current weather, strictly from this set: ['blues', 'country', 'hip hop', 'jazz', 'pop', 'reggae', 'rock']. 
    Answer in JSON with the following format (omit markdown annotations like ```json, only output valid json): {'top_music_genres': ['genre1', 'genre2', '...'], 'top_tags'=['...'], 'title_playlist':'The playlist name'}', where top_tags can only have values from this set: ["dating", "violence","world/life","night/time","shake the audience","family/gospel","romantic","communication","obscene", "family/spiritual", "sadness","feelings"]. Provide at least 3 tags
    """
    detail = "low"
    max_tokens = 300

    if api_key is None:
        raise KeyError("OPENAI_API_KEY")

    try:
        img = Image.fromarray(image)
        img = scale_image(img)

        buffered = io.BytesIO()
        img.save(buffered, format=format)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        client = OpenAI(api_key=api_key)
        payload = {
            "model": "gpt-4-turbo",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{img_base64}", "detail": detail}}
                ]
            }],
            "max_tokens": max_tokens
        }

        response = client.chat.completions.create(**payload)
        description = response.choices[0].message.content

        return ImageCaption(**eval(description))

    except Exception as e:
        with open("error_log.txt", 'a') as log_file:
            log_file.write(str(e) + '\n')
            log_file.write(traceback.format_exc() + '\n')
        return f"Error: {str(e)}"


def scale_image(img: Image):
    max_width = 2048

    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        return img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    return img


if __name__ == "__main__":
    path = "./img/death.jpeg"
    image = Image.open(path)
    image = np.array(image)

    description = generate_caption(image=image, format="JPEG", weather_desc="sunny")
    print(description)