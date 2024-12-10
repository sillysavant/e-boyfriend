# pip install openai, speechrecognition
import uuid
from dotenv import load_dotenv
import os
from elevenlabs import ElevenLabs, VoiceSettings
from openai import OpenAI
import speech_recognition as sr
import time, os, wave
load_dotenv()

# Choosing OpenAI Model
model="gpt-4o-mini"
API_KEY=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client_11lab = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

# Integration with OpenAI API
def ask(user_input):
  messages = [
        {
          "role": "system", 
          "content": "You are Alpha, My Personal AI Assistant"
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
    # Calling the text_to_speech conversion API with detailed parameters
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

def detect_wake_word():
  print("==== START DETECTING ====")

  # Accumulates the user's spoken command after detecting the wake word.
  command = ""
  # Counter to track whether a command is being captured.
  ct = 0

  # Parameters
  #file_path = f"audio/live_recording_{uuid.uuid4()}.wav"
  file_path = f"audio/live_recording.wav"
  # Duration of each audio chunk (3 seconds). -> time that goes for the transcription for detecting the alpha word
  chunk_duration = 3
  # Sampling rate for audio processing (44100 Hz).
  sample_rate = 44100
  
  recognizer = sr.Recognizer()
  last_processed_time = 0 # Tracks the last processed audio timestamp -> this will change every time the audio is transcribed
  wake_word_count = 0 # Counts the number of times the wake word is detected.
  
  while True:
    # Continuously checks if the specified file_path exists.
    if os.path.exists(file_path):
      try:
        with wave.open(file_path, 'rb') as wf:
          
          # total time of the live recording
          total_duration = wf.getnframes() / sample_rate
          # The condition checks if the total_duration of the audio file 
          # has increased enough (by at least chunk_duration) since the last_processed_time.
          # If True, this means there is a new audio chunk available to process.

          if total_duration > last_processed_time + chunk_duration:
            # set the position of the live recording at which we want to transcribe
            wf.setpos(int(last_processed_time * sample_rate))
            # record the frame of three second at which we want to transcribe
            frames = wf.readframes(int(chunk_duration * sample_rate))
            chunk_file = 'audio/chunk.wav' # Saves the current audio chunk to a temporary file 
            
            # save chunk.wav as an audio file 
            with wave.open(chunk_file, 'wb') as chunk_wf:
              chunk_wf.setnchannels(wf.getnchannels())
              chunk_wf.setsampwidth(wf.getsampwidth())
              chunk_wf.setframerate(sample_rate)
              chunk_wf.writeframes(frames)
              
              # Opens the chunk file and transcribes it 
              # using Google’s Speech Recognition API.
            with sr.AudioFile(chunk_file) as source:
                # Reads and prepares the audio data for transcription.
              audio = recognizer.record(source)
              #print(f"{last_processed_time}-{last_processed_time + chunk_duration}")
              # length of the audio
              
              try:
              #If transcription fails (e.g., unclear audio), an exception is raised and handled in the except block.
                transcript = recognizer.recognize_google(audio) # transcribed text.
                print("transcript: ", transcript)
                # Acts as a countdown timer to indicate when command capture should stop.
                # If no wake word is detected, transcribed text may be 
                # used to continue an ongoing command (if ct > 0).
                if ct>0: #If a command is being captured, alpha is detected 
                  command += transcript
                  ct -= 1
                  print("Command: " + command)
                  output = ask(command)
                  text_to_speech_file(output)
                  print(f"Alpha: {output}")
                  
                if "Alpha" in transcript:
                  ct = 0
                  command = ""
                  wake_word_count += 1
                  # enabling command capture mode.
                  ct += 1 # for more transcript for new chunk file
                  command += transcript
                  command += " "
                  print()
                  print(f"Detected No: {wake_word_count}")

              except sr.UnknownValueError:
                if ct>0:
                  ct -= 1
                  print("Command: " + command)
                  output = ask(command)
                  text_to_speech_file(output)
                  print(f"Alpha: {output}")
              except sr.RequestError as e:
                print(f"Request Error {e}")
            os.remove(chunk_file)
            last_processed_time += chunk_duration
      except EOFError:
        time.sleep(0.1)  # Allow more time for the file to finish writing
        continue
    time.sleep(0.1)

# Run the Detection
detect_wake_word()