# pip install openai, speechrecognition
import asyncio
from io import BytesIO
import uuid
from dotenv import load_dotenv
import os
from elevenlabs import ElevenLabs, VoiceSettings
from openai import OpenAI
import pvporcupine
import pyaudio
import speech_recognition as sr
import time, os, wave
load_dotenv()

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)
model="gpt-4o-mini"

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client_11lab = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

wake_word = "Alpha"

# PyAudio configuration
CHUNK = 1024  # Audio chunk size
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sampling rate in Hz

# Integration with OpenAI API
def ask(user_input):
  messages = [
        {
          "role": "system", 
          "content": f"You are {wake_word}, My Personal AI Assistant"
        },
        {
          "role": "user", 
          "content": user_input
        }
    ]
  response = client.chat.completions.create(model=model,messages= messages,max_tokens=40)
  output=response.choices[0].message.content
  return output
  
def text_to_speech_file(text: str) -> str:
    response = client_11lab.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Generating a unique file name for the output MP3 file
    save_file_path = "audio/response.mp3"
    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
                
    return save_file_path
def capture_command(stream: pyaudio.Stream, size):
  command_frames = []
  for _ in range(0, int(RATE / CHUNK) * 3): # Capture 3 seconds of audio
    audio_data = stream.read(CHUNK, exception_on_overflow=False)
    command_frames.append(audio_data)
    
  command_buffer = BytesIO()
  with wave.open(command_buffer, "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(size)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(command_frames))
  command_buffer.seek(0)
  return command_buffer
  
# async def detect_wake_word():
#   p = pyaudio.PyAudio()
#   stream = p.open(
#       format=FORMAT,
#       channels=CHANNELS,
#       rate=RATE,
#       input=True,
#       frames_per_buffer=CHUNK,
#   )
#   print("Listening for wake word...")

#   command = "" # Accumulates the user's spoken command after detecting the wake word.
#   ct = 0 # Counter to track whether a command is being captured.
#   recognizer = sr.Recognizer()
  
#   try:
#     while True:
#       frames = []
#       for _ in range(0, int(RATE / CHUNK)*5): # Capture 3 seconds of audio
#         audio_data = stream.read(CHUNK, exception_on_overflow=False)
#         frames.append(audio_data)
      
#       buffer = BytesIO()
#       with wave.open(buffer, "wb") as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(p.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))
#       buffer.seek(0)
      
#       with open("recorded_audio.wav", 'wb') as f:
#         f.write(buffer.read())
#       buffer.seek(0)
      
#       # Opens the buffer and transcribes it using Google’s Speech Recognition API.
#       with sr.AudioFile(buffer) as source:
#         # Reads and prepares the audio data for transcription.
#         audio = recognizer.record(source)
#         try:
#           transcript = recognizer.recognize_google(audio)
#           print(f"Transcript: {transcript}")
          
#           if wake_word.lower() in transcript.lower():
#             print("Wake word detected!")
            
#             command_buffer = capture_command(stream, p.get_sample_size(FORMAT))
#             transcript2 = " "
#             with sr.AudioFile(command_buffer) as source:
#               audio = recognizer.record(source)
#               transcript2 = recognizer.recognize_google(audio)
#             full_transcript = transcript + " " + transcript2
#             print(f"Full transcript: {full_transcript}")
#             response = ask(full_transcript)
#             print(f"Response: {response}")
#             text_to_speech_file(response)
#         except sr.UnknownValueError:
#           pass
#         except sr.RequestError as e:
#           print(f"Request Error {e}")
#       await asyncio.sleep(0.1)
#   except KeyboardInterrupt:
#       print("Stopping...")
#   finally:
#       stream.stop_stream()
#       stream.close()
#       p.terminate()

    
asyncio.run(detect_wake_word())