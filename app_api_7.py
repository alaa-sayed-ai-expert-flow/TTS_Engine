from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from typing import Optional
from TTS.api import TTS
from pydub import AudioSegment
from fastapi.responses import StreamingResponse, JSONResponse
import os
import re
import torch
from io import BytesIO, StringIO
from datetime import datetime
import logging
import time
import asyncio
import sqlite3
from starlette.middleware.base import BaseHTTPMiddleware
from cryptography.fernet import Fernet
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
def get_client_ip():
    try:
        # Use httpbin to fetch client IP (not recommended for production apps)
        response = requests.get('https://httpbin.org/ip')
        ip = response.json()['origin']
        return ip
    except:
        return 'Unknown'

client_ip = get_client_ip()
# Setup logging to capture logs and save to a file
log_file = "system_logs.log"
log_dir = "system_logs"  # Directory for log files
base_filename = "system_logs"  # Base file name
max_bytes = 1024 * 10  # 10 KB per log file (adjustable)
max_files = 5  # Keep up to 5 log files (adjustable)
# Initialize SQL Database for logging
db_file = "api_logs.db"
conn = sqlite3.connect(db_file)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             date_time TEXT,
             client_ip TEXT,
             method TEXT,
             url TEXT,
             duration REAL,
             status TEXT,
             request_content TEXT,
             error_message TEXT,
             characters_count INTEGER)''')
conn.commit()

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', filemode="a")

app = FastAPI(title="Text-to-Speech API", description="API to convert text to speech with selectable language, gender, and speaker.")

# Path to your speaker files (Update this to the actual path where your audio samples are stored)
speaker_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")

# Available options
LANGUAGES = ["ar", "en"]
GENDERS = ["Female", "Male"]
FEMALE_SPEAKERS = ["Aisha", "Fatima", "Alyaa", "Angel", "Youstina"]
MALE_SPEAKERS = ["Omar", "Ali"]
AUDIO_FORMATS = ["normal", "16kbps_mono_pcm_wav", "32kbps_stereo_aac_m4a", "16kbps_mono_opus_opus", "64kbps_mono_mp3", "8kbps_mono_ulaw_wav"]



# Cache the TTS model to avoid reloading
@app.on_event("startup")
def load_tts_model():
    global tts
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS(model_name="xtts_v2.0.2", gpu=(device == "cuda"))
    print(f"TTS model loaded on {device}")

# Pydantic model for request
class TTSRequest(BaseModel):
    language: str
    gender: str
    speaker: str
    text: str

# Function to split text into sentences
def split_text_to_sentences(text):
    cleaned_text = re.sub(r'\s+', ' ', text).replace('\n', ' ').strip()
    sentence_boundaries = re.compile(r'(?<=[.!?]) +')
    sentences = sentence_boundaries.split(cleaned_text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


# Function to append a log entry to the SQL database
def append_sql_log(client_ip, method, url, duration, status, request_content, error_message, characters_count):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    print(f"Iam recording that in sql : {client_ip, method, url, duration, status, request_content, error_message, characters_count}")
    request_content = str(request_content)
    c.execute("INSERT INTO logs (date_time, client_ip, method, url, duration, status, request_content, error_message, characters_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), client_ip, method, url, duration, status,request_content, error_message, characters_count))
    conn.commit()
    conn.close()
    
def append_log_message(log_message, log_dir, base_filename, max_bytes, max_files):
    """
    Appends a log message to a rolling log file.

    Args:
        log_message (str): The message to log.
        log_dir (str): Directory where log files will be stored.
        base_filename (str): Base name for log files.
        max_bytes (int): Maximum size of each log file in bytes.
        max_files (int): Maximum number of log files to keep.
    """
    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Generate full log file path for the current file
    log_file = os.path.join(log_dir, f"{base_filename}.log")

    # Check if the current log file exceeds the size limit
    if os.path.exists(log_file) and os.path.getsize(log_file) >= max_bytes:
        # Perform file rotation
        rotate_files(log_dir, base_filename, max_files)

    # Append the log message with timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding='utf-8') as log_file:
        log_file.write(f"{current_time} - {log_message}\n")
        print("Log message sent successfully.")


def rotate_files(log_dir, base_filename, max_files):
    """
    Rotates log files, keeping a limited number of backups.

    Args:
        log_dir (str): Directory where log files are stored.
        base_filename (str): Base name for log files.
        max_files (int): Maximum number of log files to keep.
    """
    # Rotate existing log files
    for i in range(max_files - 1, 0, -1):
        older_log_file = os.path.join(log_dir, f"{base_filename}.{i}.log")
        newer_log_file = os.path.join(log_dir, f"{base_filename}.{i - 1}.log")

        # If the older log file already exists, remove it to avoid FileExistsError
        if os.path.exists(older_log_file):
            os.remove(older_log_file)

        # Rename the newer log file if it exists
        if os.path.exists(newer_log_file):
            os.rename(newer_log_file, older_log_file)

    # Rename the base log file to start the sequence
    current_log_file = os.path.join(log_dir, f"{base_filename}.log")
    first_backup_log_file = os.path.join(log_dir, f"{base_filename}.0.log")

    # If the first backup file exists, remove it before renaming
    if os.path.exists(first_backup_log_file):
        os.remove(first_backup_log_file)

    if os.path.exists(current_log_file):
        os.rename(current_log_file, first_backup_log_file)

# Function to get speaker file path
def get_speaker_file(gender, speaker):
    if gender not in GENDERS:
        append_log_message("Invalid gender selected.", log_dir, base_filename, max_bytes, max_files)

        raise ValueError("Invalid gender selected.")
    if gender == "Female":
        if speaker not in FEMALE_SPEAKERS:
            append_log_message("Invalid female speaker selected.", log_dir, base_filename, max_bytes, max_files)
            raise ValueError("Invalid female speaker selected.")
        speaker_files = {
            "Aisha": "Female.wav",
            "Fatima": "Female_1.wav",
            "Alyaa": "Female_2.wav",
            "Angel": "Female_3.wav",
            "Youstina": "Female_4.wav",
        }
    else:
        if speaker not in MALE_SPEAKERS:
            append_log_message("Invalid male speaker selected.", log_dir, base_filename, max_bytes, max_files)
            raise ValueError("Invalid male speaker selected.")
        speaker_files = {
            "Omar": "Male.wav",
            "Ali": "Male_1.wav",
        }

    speaker_file = os.path.join(speaker_base_path, speaker_files.get(speaker))
    if not os.path.exists(speaker_file):
        raise FileNotFoundError(f"Speaker file '{speaker_file}' not found.")

    return speaker_file

#"16kbps_mono_pcm_wav", "32kbps_stereo_aac_m4a", "16kbps_mono_opus_opus", "64kbps_mono_mp3", "8kbps_mono_ulaw_wav"
def export_audio_formats(combined_audio , format):
    buffer = BytesIO()
    if format == "16kbps_mono_pcm_wav":
        # Export to 16kbps, mono, PCM .wav
        buffer = BytesIO()
        pcm_wav = combined_audio.set_frame_rate(16000).set_channels(1)
        pcm_wav.export(buffer, format="wav", codec="pcm_s16le")
        buffer.seek(0)
    if format == "32kbps_stereo_aac_m4a":
        # Export to 32kbps, stereo, AAC .m4a
        buffer = BytesIO()
        aac_m4a = combined_audio.set_frame_rate(32000).set_channels(2)
        aac_m4a.export(buffer, format="mp3", bitrate="32k")
        buffer.seek(0)
    if format == "16kbps_mono_opus_opus":
        # Export to 16kbps, mono, Opus .opus
        buffer = BytesIO()
        opus_audio = combined_audio.set_frame_rate(16000).set_channels(1)
        opus_audio.export(buffer, format="opus", bitrate="16k")
        buffer.seek(0)
    if format == "64kbps_mono_mp3":
        # Export to 64kbps, mono, MP3 .mp3
        buffer = BytesIO()
        mp3_audio = combined_audio.set_frame_rate(64000).set_channels(1)
        mp3_audio.export(buffer, format="mp3", bitrate="64k")
        buffer.seek(0)
    if format == "8kbps_mono_ulaw_wav":
        # Export to 8kbps, mono, u-law PCM .wav
        buffer = BytesIO()
        ulaw_wav = combined_audio.set_frame_rate(8000).set_channels(1)
        ulaw_wav.export(buffer, format="wav", codec="pcm_mulaw", bitrate="8k")
        buffer.seek(0)
    return buffer
# Middleware to log request details
class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        log_data = {
            "date_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "duration": f"{process_time:.4f} seconds"
        }
        append_log_message(f"Request: {log_data}", log_dir, base_filename, max_bytes, max_files)
        print(f"### Request: {log_data}")
        return response
def clean_text_for_log_file(text):
    # Clean the text by removing unwanted characters (keeping only Arabic, numbers, and basic punctuation)
    cleaned_text = re.sub(r'[^\u0600-\u06FF0-9،٫؟:.٪٪ ]+', '', text)
    return cleaned_text

app.add_middleware(LogRequestMiddleware)




# API Endpoint
@app.post("/generate-voice", summary="Generate voice from text")
async def generate_voice(
        request: Request,
        language: str = Form(..., description="Language code (e.g., 'ar', 'en')"),
        gender: str = Form(..., description="Gender ('Female' or 'Male')"),
        speaker: str = Form(..., description="Speaker name based on gender"),
        text: str = Form(..., description="Text to convert to speech"),
        format: str = Form(..., description="Audio format for output (16kbps_mono_pcm_wav, 32kbps_stereo_aac_m4a, 16kbps_mono_opus_opus, 64kbps_mono_mp3, 8kbps_mono_ulaw_wav)"),
        allowance: str = Form("Yes", description="Allowance to generate voice (Yes or No)")  # Add allowance parameter
):
    # Check allowance before proceeding
    if allowance == "No":
        append_log_message(
            f"Request from {client_ip} rejected due to exceeding the concurrent request limit.",
            log_dir, base_filename, max_bytes, max_files)

        append_sql_log(client_ip, "POST", "/generate-voice",
                       "No-duration",
                       "403", "no_content",
                       "License limit for concurrent requests exceeded", int(0))
        raise HTTPException(status_code=403, detail="License limit for concurrent requests exceeded")

    else:
        start_time = time.time()

        try:
            # Validate inputs
            if language not in LANGUAGES:
                append_log_message(
                    f"Request from {client_ip} not completed because of Entered unsupported language {language} , So User was told to Choose from {LANGUAGES} .",
                    log_dir, base_filename, max_bytes, max_files)
                append_sql_log(client_ip, "POST", "/generate-voice",
                               "No-duration - unsupported language",
                               "400", "no_content",
                               f"Request from {client_ip} not completed \nbecause of Entered unsupported language {language}\n , So User was told to Choose from {LANGUAGES} .",
                               0)
                print(
                    f"### Request from {client_ip} not completed because of Entered unsupported language {language} , So User was told to Choose from {LANGUAGES} .")
                raise HTTPException(status_code=400, detail=f"Unsupported language. Choose from {LANGUAGES}.")

            if gender not in GENDERS:
                append_log_message(
                    f"Request from {client_ip} not completed because of Entered unsupported gender {gender} , So User was told to Choose from {GENDERS} .",
                    log_dir, base_filename, max_bytes, max_files)
                append_sql_log(client_ip, "POST", "/generate-voice",
                               "No-duration - unsupported gender",
                               "400",
                               "no_content",
                               f"Request from {client_ip} not completed \nbecause of Entered unsupported gender {gender} , \nSo User was told to Choose from {GENDERS} .",
                               0)
                print(
                    f"### Request from {client_ip} not completed because of Entered unsupported gender {gender} , So User was told to Choose from {GENDERS} .")
                raise HTTPException(status_code=400, detail=f"Unsupported gender. Choose from {GENDERS}.")

            if gender == "Female" and speaker not in FEMALE_SPEAKERS:
                append_log_message(
                    f"Request from {client_ip} not completed because of Entered unsupported famale speaker: {speaker} , So User was told to Choose from {FEMALE_SPEAKERS} .",
                    log_dir, base_filename, max_bytes, max_files)
                append_sql_log(client_ip, "POST", "/generate-voice",
                               "No-duration - unsupported female speaker",
                               "400",
                               "no_content",
                               f"Request from {client_ip} not completed \nbecause of entered unsupported famale speaker {speaker} , \nSo User was told to Choose from {FEMALE_SPEAKERS} .",
                               0)
                print(
                    f"### Request from {client_ip} not completed because of Entered unsupported famale speaker: {speaker} , So User was told to Choose from {FEMALE_SPEAKERS} .")
                raise HTTPException(status_code=400,
                                    detail=f"Unsupported female speaker. Choose from {FEMALE_SPEAKERS}.")

            if gender == "Male" and speaker not in MALE_SPEAKERS:
                append_log_message(
                    f"Request from {client_ip} not completed because of Entered unsupported male speaker: {speaker} , So User was told to Choose from {MALE_SPEAKERS} .",
                    log_dir, base_filename, max_bytes, max_files)
                append_sql_log(client_ip, "POST", "/generate-voice",
                               "No-duration - unsupported male speaker",
                               "400",
                               "no_content",
                               f"Request from {client_ip} not completed \nbecause of entered unsupported male speaker {speaker} , \nSo User was told to Choose from {MALE_SPEAKERS} .",
                               0)
                print(
                    f"### Request from {client_ip} not completed because of Entered unsupported male speaker: {speaker} , So User was told to Choose from {MALE_SPEAKERS} .")
                raise HTTPException(status_code=400,
                                    detail=f"Unsupported male speaker. Choose from {MALE_SPEAKERS}.")

            if not text.strip():
                append_log_message(
                    f"Request from {client_ip} not completed because User didn't enter text .", log_dir,
                    base_filename, max_bytes, max_files)
                append_sql_log(client_ip, "POST", "/generate-voice",
                               "No-duration - no text entered",
                               "400",
                               "no_content",
                               f"Request from {client_ip} not completed \nbecause User didn't enter text .",
                               0)
                print(
                    f"### Request from {client_ip} not completed because User didn't enter text .")
                raise HTTPException(status_code=400, detail="Text cannot be empty.")

            if format not in AUDIO_FORMATS:
                append_log_message(
                    f"Request from {client_ip} not completed because User entered unsupported format from these {AUDIO_FORMATS} .",
                    log_dir, base_filename, max_bytes, max_files)
                append_sql_log(client_ip, "POST", "/generate-voice",
                               "No-duration - unsupported format ",
                               "400",
                               "no_content",
                               f"Request from {client_ip} not completed \nbecause User entered unsupported format. ",
                               0)
                raise HTTPException(status_code=400, detail=f"Unsupported format. Choose from {AUDIO_FORMATS}.")

            # Get speaker file
            speaker_file = get_speaker_file(gender, speaker)
            characters_count = len(text)
            # Split text into sentences
            sentences = split_text_to_sentences(text)
            audio_segments = []

            for i, sentence in enumerate(sentences):
                output_path = f"generated_output_{i}.wav"
                # Configurations for male and female voices
                if language == "ar" and gender == "Female":
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
                elif language == "ar" and gender == "Male":
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

            # Concatenate all audio segments
            combined_audio = AudioSegment.silent(duration=0)
            for audio_file in audio_segments:
                combined_audio += AudioSegment.from_wav(audio_file)
                os.remove(audio_file)  # Clean up individual files

            # Export combined audio to bytes
            buffer = BytesIO()
            if format == "normal":
                # print("############## The voice is combining .... ")
                combined_audio.export(buffer, format="wav")
                buffer.seek(0)
                # print("############## The voice is combined successfully .... ")
            else:
                buffer = export_audio_formats(combined_audio, format)

            # Log the execution duration
            duration = time.time() - start_time
            request_content = {
                'language': language,
                'gender': gender,
                'speaker': speaker,
                'text': text,
                'format': format
            }

            append_log_message(
                f"Request from {client_ip} completed in {duration:.2f} seconds. \n request_content: {str(request_content)}",
                log_dir, base_filename, max_bytes, max_files)
            append_sql_log(client_ip, "POST", "/generate-voice", duration, "200", request_content,
                           f"No Error Voice generated successfully in format : {format}", characters_count)
            print(f"### Request from {client_ip} completed in {duration:.2f} seconds.")

            return StreamingResponse(buffer, media_type="audio/wav",
                                     headers={"Content-Disposition": "attachment; filename=generated_voice.wav"})

        except HTTPException as he:
            logging.error(f"HTTP Exception: {str(he.detail)}")
            return JSONResponse(content={
                "detail": he.detail
            }, status_code=he.status_code)

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return JSONResponse(content={
                "detail": f"An unexpected error occurred: {str(e)}"
            }, status_code=500)

# @app.post("/generate-voice", summary="Generate voice from text")
# async def generate_voice(
#         request: Request,
#         language: str = Form(..., description="Language code (e.g., 'ar', 'en')"),
#         gender: str = Form(..., description="Gender ('Female' or 'Male')"),
#         speaker: str = Form(..., description="Speaker name based on gender"),
#         text: str = Form(..., description="Text to convert to speech"),
#         format: str = Form(..., description="Audio format for output (16kbps_mono_pcm_wav, 32kbps_stereo_aac_m4a, 16kbps_mono_opus_opus, 64kbps_mono_mp3, 8kbps_mono_ulaw_wav)")
#
# ):
#     async with semaphore:  # Limit concurrent requests
#         start_time = time.time()
#
#         try:
#             # Validate inputs
#             if language not in LANGUAGES:
#                 append_log_message(
#                     f"Request from {request.client.host} not completed because of Entered unsupported language {language} , So User was told to Choose from {LANGUAGES} .",
#                     log_dir, base_filename, max_bytes, max_files)
#                 append_sql_log(request.client.host, "POST", "/generate-voice",
#                                "There is no duration because request didn't complete because of unsupported language",
#                                "400", "no_content",
#                                f"Request from {request.client.host} not completed because of Entered unsupported language {language} , So User was told to Choose from {LANGUAGES} .",
#                                0)
#                 print(
#                     f"### Request from {request.client.host} not completed because of Entered unsupported language {language} , So User was told to Choose from {LANGUAGES} .")
#                 raise HTTPException(status_code=400, detail=f"Unsupported language. Choose from {LANGUAGES}.")
#
#             if gender not in GENDERS:
#                 append_log_message(
#                     f"Request from {request.client.host} not completed because of Entered unsupported gender {gender} , So User was told to Choose from {GENDERS} .",
#                     log_dir, base_filename, max_bytes, max_files)
#                 append_sql_log(request.client.host, "POST", "/generate-voice",
#                                "There is no duration because request didn't complete because of unsupported gender",
#                                "400",
#                                "no_content",
#                                f"Request from {request.client.host} not completed because of Entered unsupported gender {gender} , So User was told to Choose from {GENDERS} .",
#                                0)
#                 print(
#                     f"### Request from {request.client.host} not completed because of Entered unsupported gender {gender} , So User was told to Choose from {GENDERS} .")
#                 raise HTTPException(status_code=400, detail=f"Unsupported gender. Choose from {GENDERS}.")
#
#             if gender == "Female" and speaker not in FEMALE_SPEAKERS:
#                 append_log_message(
#                     f"Request from {request.client.host} not completed because of Entered unsupported famale speaker: {speaker} , So User was told to Choose from {FEMALE_SPEAKERS} .",
#                     log_dir, base_filename, max_bytes, max_files)
#                 append_sql_log(request.client.host, "POST", "/generate-voice",
#                                "There is no duration because request didn't complete because of unsupported female speaker",
#                                "400",
#                                "no_content",
#                                f"Request from {request.client.host} not completed because of entered unsupported famale speaker {speaker} , So User was told to Choose from {FEMALE_SPEAKERS} .",
#                                0)
#                 print(
#                     f"### Request from {request.client.host} not completed because of Entered unsupported famale speaker: {speaker} , So User was told to Choose from {FEMALE_SPEAKERS} .")
#                 raise HTTPException(status_code=400,
#                                     detail=f"Unsupported female speaker. Choose from {FEMALE_SPEAKERS}.")
#
#             if gender == "Male" and speaker not in MALE_SPEAKERS:
#                 append_log_message(
#                     f"Request from {request.client.host} not completed because of Entered unsupported male speaker: {speaker} , So User was told to Choose from {MALE_SPEAKERS} .",
#                     log_dir, base_filename, max_bytes, max_files)
#                 append_sql_log(request.client.host, "POST", "/generate-voice",
#                                "There is no duration because request didn't complete because of unsupported male speaker",
#                                "400",
#                                "no_content",
#                                f"Request from {request.client.host} not completed because of entered unsupported male speaker {speaker} , So User was told to Choose from {MALE_SPEAKERS} .",
#                                0)
#                 print(
#                     f"### Request from {request.client.host} not completed because of Entered unsupported male speaker: {speaker} , So User was told to Choose from {MALE_SPEAKERS} .")
#                 raise HTTPException(status_code=400,
#                                     detail=f"Unsupported male speaker. Choose from {MALE_SPEAKERS}.")
#
#             if not text.strip():
#                 append_log_message(
#                     f"Request from {request.client.host} not completed because User didn't enter text .", log_dir,
#                     base_filename, max_bytes, max_files)
#                 append_sql_log(request.client.host, "POST", "/generate-voice",
#                                "There is no duration because request didn't complete because of no text entered",
#                                "400",
#                                "no_content",
#                                f"Request from {request.client.host} not completed because User didn't enter text .",
#                                0)
#                 print(
#                     f"### Request from {request.client.host} not completed because User didn't enter text .")
#                 raise HTTPException(status_code=400, detail="Text cannot be empty.")
#
#             if format not in AUDIO_FORMATS:
#                 append_log_message(
#                     f"Request from {request.client.host} not completed because User entered unsupported format from these {AUDIO_FORMATS} .",
#                     log_dir, base_filename, max_bytes, max_files)
#                 append_sql_log(request.client.host, "POST", "/generate-voice",
#                                "There is no duration because request didn't complete because User entered unsupported format ",
#                                "400",
#                                "no_content",
#                                f"Request from {request.client.host} not completed because User entered unsupported format from these {AUDIO_FORMATS} ",
#                                0)
#                 raise HTTPException(status_code=400, detail=f"Unsupported format. Choose from {AUDIO_FORMATS}.")
#
#             # Get speaker file
#             speaker_file = get_speaker_file(gender, speaker)
#             characters_count = len(text)
#             # Split text into sentences
#             sentences = split_text_to_sentences(text)
#             audio_segments = []
#
#             for i, sentence in enumerate(sentences):
#                 output_path = f"generated_output_{i}.wav"
#                 # Configurations for male and female voices
#                 if language == "ar" and gender == "Female":
#                     temperature = 0.1
#                     repetition_penalty = 50.5
#                     top_k = 80
#                     # Generate the TTS output
#                     tts.tts_to_file(
#                         text=sentence,
#                         speaker_wav=speaker_file,
#                         language=language,
#                         file_path=output_path,
#                         split_sentences=True,
#                         temperature=temperature,
#                         repetition_penalty=repetition_penalty,
#                         top_k=top_k,
#                         top_p=0.95,
#                         speed=1.0
#                     )
#                 elif language == "ar" and gender == "Male":
#                     temperature = 0.1
#                     repetition_penalty = 10.5
#                     top_k = 80
#                     # Generate the TTS output
#                     tts.tts_to_file(
#                         text=sentence,
#                         speaker_wav=speaker_file,
#                         language=language,
#                         file_path=output_path,
#                         split_sentences=True,
#                         temperature=temperature,
#                         repetition_penalty=repetition_penalty,
#                         top_k=top_k,
#                         top_p=0.95,
#                         speed=1.0
#                     )
#                 else:
#                     # Generate the TTS output
#                     tts.tts_to_file(
#                         text=sentence,
#                         speaker_wav=speaker_file,
#                         language=language,
#                         file_path=output_path,
#                         split_sentences=True,
#                     )
#                 audio_segments.append(output_path)
#
#             # Concatenate all audio segments
#             combined_audio = AudioSegment.silent(duration=0)
#             for audio_file in audio_segments:
#                 combined_audio += AudioSegment.from_wav(audio_file)
#                 os.remove(audio_file)  # Clean up individual files
#
#             # Export combined audio to bytes
#             buffer = BytesIO()
#             if format == "normal":
#                 # print("############## The voice is combining .... ")
#                 combined_audio.export(buffer, format="wav")
#                 buffer.seek(0)
#                 # print("############## The voice is combined successfully .... ")
#             else:
#                 buffer = export_audio_formats(combined_audio, format)
#
#             # Log the execution duration
#             duration = time.time() - start_time
#             request_content = {
#                 'language': language,
#                 'gender': gender,
#                 'speaker': speaker,
#                 'text': text,
#                 'format': format
#             }
#
#             append_log_message(
#                 f"Request from {request.client.host} completed in {duration:.2f} seconds. \n request_content: {str(request_content)}",
#                 log_dir, base_filename, max_bytes, max_files)
#             append_sql_log(request.client.host, "POST", "/generate-voice", duration, "200", request_content,
#                            f"No Error Voice generated successfully in format : {format}", characters_count)
#             print(f"### Request from {request.client.host} completed in {duration:.2f} seconds.")
#
#             return StreamingResponse(buffer, media_type="audio/wav",
#                                      headers={"Content-Disposition": "attachment; filename=generated_voice.wav"})
#
#         except HTTPException as he:
#             logging.error(f"HTTP Exception: {str(he.detail)}")
#             return JSONResponse(content={
#                 "detail": he.detail
#             }, status_code=he.status_code)
#
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             return JSONResponse(content={
#                 "detail": f"An unexpected error occurred: {str(e)}"
#             }, status_code=500)




