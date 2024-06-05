import streamlit as st
from PIL import Image
import numpy as np

from csvLookup import get_top_songs
from imgCaption import generate_caption

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    img = Image.open(img_file_buffer)

    img_array = np.array(img)

    st.write("Preparing your playlist...")

    caption = generate_caption(img_array, format="PNG", weather_desc="sunny")

    st.header("Description")
    st.write(caption)

    csv_songs = get_top_songs(caption)
    st.header("Songs from csv")
    st.write(csv_songs)
