# import streamlit as st
# import torch
# from TTS.api import TTS
# import io
# from pydub import AudioSegment
# import re
#
#
# # Cache the model to avoid reloading it multiple times
# @st.cache_resource
# def load_tts_model():
#     # Get device
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     # Load model
#     tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True).to(device)
#     return tts
#
#
# # Function to convert uploaded audio file to WAV format
# def convert_to_wav(uploaded_audio):
#     audio = AudioSegment.from_file(uploaded_audio)
#     wav_buffer = io.BytesIO()
#     audio.export(wav_buffer, format="wav")
#     return wav_buffer
#
#
# # Function to split text into sentences
# def split_text_to_sentences(text):
#     cleaned_text = re.sub(r'\s+', ' ', text).replace('\n', ' ').strip()
#     sentence_boundaries = re.compile(r'(?<=[.!?]) +')
#     sentences = sentence_boundaries.split(cleaned_text)
#     return [sentence.strip() for sentence in sentences if sentence.strip()]
#
#
# # Function to concatenate audio segments
# def concatenate_audios(audio_files):
#     combined = AudioSegment.silent(duration=0)
#     for audio_file in audio_files:
#         combined += AudioSegment.from_wav(audio_file)
#     return combined
#
#
# # Streamlit app layout
# st.title("Text to Speech System with Voice Sample Upload")
#
# # Load the TTS model only once
# tts = load_tts_model()
#
# # Language selection dropdown
# language = st.selectbox("Select language:", ["ar", "en"])
#
# # Gender selection dropdown
# gender = st.selectbox("Select gender:", ["Female", "Male"])
#
# # Speaker selection based on gender
# if gender == "Female":
#     speaker = st.selectbox("Select speaker:", ["Aisha", "Fatima"])
#     speaker_wav = "Female.wav" if speaker == "Aisha" else "Female_1.wav"
# else:
#     speaker = st.selectbox("Select speaker:", ["Omar", "Ali"])
#     speaker_wav = "Male.wav" if speaker == "Omar" else "Male_1.wav"
#
# # Text input (no character limit)
# text = st.text_area("Enter text to generate speech:")
#
# # Upload sample voice (accepting any audio format)
# uploaded_file = st.file_uploader("Upload a voice sample (any format):",
#                                  type=["wav", "mp3", "ogg", "flac", "aac", "m4a"])
#
# if uploaded_file is not None:
#     converted_wav_buffer = convert_to_wav(uploaded_file)
#     with open("converted_speaker.wav", "wb") as f:
#         f.write(converted_wav_buffer.getvalue())
#     st.success("Your uploaded voice is converted to WAV and ready for the system.")
#     st.audio(converted_wav_buffer.getvalue(), format="audio/wav")
#
# # Generate speech button
# if st.button("Generate Speech"):
#     if uploaded_file is not None and text:
#         text_sentences = split_text_to_sentences(text)
#         audio_segments = []
#
#         for i, sentence in enumerate(text_sentences):
#             output_path = f"generated_output_{i}.wav"
#
#             # Configurations for male and female voices
#             if gender == "Female":
#                 temperature = 0.1
#                 repetition_penalty = 50.5
#             else:
#                 temperature = 0.2
#                 repetition_penalty = 10.5
#
#             # Generate the TTS output
#             tts.tts_to_file(
#                 text=sentence,
#                 speaker_wav="converted_speaker.wav",
#                 language=language,
#                 file_path=output_path,
#                 split_sentences=False,
#                 temperature=temperature,
#                 repetition_penalty=repetition_penalty,
#                 top_k=80,
#                 top_p=0.95,
#                 speed=1.0
#             )
#             audio_segments.append(output_path)
#             st.write(f"Sentence {i + 1}: '{sentence}' is generated successfully.")
#
#         combined_audio = concatenate_audios(audio_segments)
#         combined_output_path = "final_output.wav"
#         combined_audio.export(combined_output_path, format="wav")
#
#         with open(combined_output_path, "rb") as f:
#             audio_bytes = f.read()
#         st.audio(audio_bytes, format="audio/wav")
#         st.download_button("Download Combined Audio", audio_bytes, file_name="final_output.wav")
#     else:
#         st.warning("Please upload a voice sample and enter some text.")

########################################################################################### Without Attention mask ######################################################################
# import streamlit as st
# import torch
# from TTS.api import TTS
# import io
# from pydub import AudioSegment
# import re
# import os
#
# # Path to your speaker files
# speaker_base_path = r"C:\Users\thegh\Python Projects\Expertflow\UnderProgress\XTTS\Samples"
#
#
# # Cache the model to avoid reloading it multiple times
# @st.cache_resource
# def load_tts_model():
#     # Get device
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     # Load model
#     tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True).to(device)
#     return tts
#
#
# # Function to split text into sentences
# def split_text_to_sentences(text):
#     cleaned_text = re.sub(r'\s+', ' ', text).replace('\n', ' ').strip()
#     sentence_boundaries = re.compile(r'(?<=[.!?]) +')
#     sentences = sentence_boundaries.split(cleaned_text)
#     return [sentence.strip() for sentence in sentences if sentence.strip()]
#
#
# # Function to concatenate audio segments
# def concatenate_audios(audio_files):
#     combined = AudioSegment.silent(duration=0)
#     for audio_file in audio_files:
#         combined += AudioSegment.from_wav(audio_file)
#     return combined
#
#
# # Streamlit app layout
# st.title("Text to Speech System")
#
# # Load the TTS model only once
# tts = load_tts_model()
#
# # Language selection dropdown
# language = st.selectbox("Select language:", ["ar", "en"])
#
# # Gender selection dropdown
# gender = st.selectbox("Select gender:", ["Female", "Male"])
#
# # Speaker selection based on gender
# if gender == "Female":
#     speaker = st.selectbox("Select speaker:", ["Aisha", "Fatima"])
#     speaker_file = os.path.join(speaker_base_path, "Female.wav") if speaker == "Aisha" else os.path.join(
#         speaker_base_path, "Female_1.wav")
# else:
#     speaker = st.selectbox("Select speaker:", ["Omar", "Ali"])
#     speaker_file = os.path.join(speaker_base_path, "Male.wav") if speaker == "Omar" else os.path.join(speaker_base_path,
#                                                                                                       "Male_1.wav")
#
# # Let the user listen to the selected speaker
# if os.path.exists(speaker_file):
#     with open(speaker_file, "rb") as f:
#         speaker_audio = f.read()
#     st.audio(speaker_audio, format="audio/wav", start_time=0)
# else:
#     st.error(f"Speaker file '{speaker_file}' not found.")
#
# # Text input (no character limit)
# text = st.text_area("Enter text to generate speech:")
#
# # Generate speech button
# if st.button("Generate Speech"):
#     if text:
#         text_sentences = split_text_to_sentences(text)
#         audio_segments = []
#
#         for i, sentence in enumerate(text_sentences):
#             output_path = f"generated_output_{i}.wav"
#
#             # Configurations for male and female voices
#             if gender == "Female":
#                 temperature = 0.1
#                 repetition_penalty = 50.5
#                 top_k = 80
#             else:
#                 temperature = 0.1
#                 repetition_penalty = 10.5
#                 top_k = 80
#
#             # Generate the TTS output
#             tts.tts_to_file(
#                 text=sentence,
#                 speaker_wav=speaker_file,
#                 language=language,
#                 file_path=output_path,
#                 split_sentences=False,
#                 temperature=temperature,
#                 repetition_penalty=repetition_penalty,
#                 top_k=top_k,
#                 top_p=0.95,
#                 speed=1.0
#             )
#             audio_segments.append(output_path)
#             st.write(f"Sentence {i + 1}: '{sentence}' is generated successfully.")
#
#         combined_audio = concatenate_audios(audio_segments)
#         combined_output_path = "final_output.wav"
#         combined_audio.export(combined_output_path, format="wav")
#
#         with open(combined_output_path, "rb") as f:
#             audio_bytes = f.read()
#         st.audio(audio_bytes, format="audio/wav")
#         st.download_button("Download Combined Audio", audio_bytes, file_name="final_output.wav")
#     else:
#         st.warning("Please enter some text.")



import streamlit as st
import torch
from TTS.api import TTS
import io
from pydub import AudioSegment
import re
import os

# os.environ['TORCH_USE_CUDA_DSA'] = '1'
# Path to your speaker files
speaker_base_path = r"C:\Users\thegh\Python Projects\Expertflow\UnderProgress\XTTS\Samples"

# Cache the model to avoid reloading it multiple times
@st.cache_resource
def load_tts_model():
    # Get device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Load model with GPU support
    #tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    tts = TTS(model_name="xtts_v2.0.2", gpu=True).to(device)
    #tts = TTS(model_name = "tts_models/multilingual/multi-dataset/bark").to(device)
    return tts

# Function to split text into sentences
def split_text_to_sentences(text):
    cleaned_text = re.sub(r'\s+', ' ', text).replace('\n', ' ').strip()
    sentence_boundaries = re.compile(r'(?<=[.!?]) +')
    sentences = sentence_boundaries.split(cleaned_text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

# Function to concatenate audio segments
def concatenate_audios(audio_files):
    combined = AudioSegment.silent(duration=0)
    for audio_file in audio_files:
        combined += AudioSegment.from_wav(audio_file)
    return combined

# Streamlit app layout
st.title("Text to Speech System")

# Load the TTS model only once
tts = load_tts_model()

# Language selection dropdown
language = st.selectbox("Select language:", ["ar", "en"])

# Gender selection dropdown
gender = st.selectbox("Select gender:", ["Female", "Male"])

# Speaker selection based on gender
if gender == "Female":
    speaker = st.selectbox("Select speaker:", ["Aisha", "Fatima" , "Alyaa" , "Angel" , "Youstina"])
    # speaker_file = os.path.join(speaker_base_path, "Female.wav") if speaker == "Aisha" else os.path.join(
    #     speaker_base_path, "Female_1.wav")
    # Define the path based on the selected speaker
    if speaker == "Aisha":
        speaker_file = os.path.join(speaker_base_path, "Female.wav")
    elif speaker == "Fatima":
        speaker_file = os.path.join(speaker_base_path, "Female_1.wav")
    elif speaker == "Alyaa":
        speaker_file = os.path.join(speaker_base_path, "Female_2.wav")
    elif speaker == "Angel":
        speaker_file = os.path.join(speaker_base_path, "Female_3.wav")
    elif speaker == "Youstina":
        speaker_file = os.path.join(speaker_base_path, "Female_4.wav")
else:
    speaker = st.selectbox("Select speaker:", ["Omar", "Ali"])
    speaker_file = os.path.join(speaker_base_path, "Male.wav") if speaker == "Omar" else os.path.join(speaker_base_path,
                                                                                                      "Male_1.wav")

# Let the user listen to the selected speaker
if os.path.exists(speaker_file):
    with open(speaker_file, "rb") as f:
        speaker_audio = f.read()
    #st.audio(speaker_audio, format="audio/wav", start_time=0)
else:
    st.error(f"Speaker file '{speaker_file}' not found.")

# Text input (no character limit)
text = st.text_area("Enter text to generate speech:")

# Generate speech button
if st.button("Generate Speech"):
    if text:
        text_sentences = split_text_to_sentences(text)
        audio_segments = []

        for i, sentence in enumerate(text_sentences):
            output_path = f"generated_output_{i}.wav"

            # Configurations for male and female voices
            if language== "ar" and gender == "Female":
                temperature = 0.1
                repetition_penalty = 50.5
                top_k = 80
                # Generate the TTS output
                tts.tts_to_file(
                    text=sentence,
                    speaker_wav=speaker_file,
                    language=language,
                    file_path=output_path,
                    split_sentences=True,
                    temperature=temperature,
                    repetition_penalty=repetition_penalty,
                    top_k=top_k,
                    top_p=0.95,
                    speed=1.0
                )
            elif language== "ar" and gender == "Male":
                temperature = 0.1
                repetition_penalty = 10.5
                top_k = 80
                # Generate the TTS output
                tts.tts_to_file(
                    text=sentence,
                    speaker_wav=speaker_file,
                    language=language,
                    file_path=output_path,
                    split_sentences=True,
                    temperature=temperature,
                    repetition_penalty=repetition_penalty,
                    top_k=top_k,
                    top_p=0.95,
                    speed=1.0
                )
            else:
                # Generate the TTS output
                tts.tts_to_file(
                    text=sentence,
                    speaker_wav=speaker_file,
                    language=language,
                    file_path=output_path,
                    split_sentences=True,
                )


            audio_segments.append(output_path)
            st.write(f"Sentence {i + 1}: '{sentence}' is generated successfully.")

        combined_audio = concatenate_audios(audio_segments)
        combined_output_path = "final_output.wav"
        combined_audio.export(combined_output_path, format="wav")

        with open(combined_output_path, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/wav")
        st.download_button("Download Combined Audio", audio_bytes, file_name="final_output.wav")
    else:
        st.warning("Please enter some text.")

