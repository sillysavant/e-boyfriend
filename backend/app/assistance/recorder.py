import pyaudio
import wave

# Parameters for audio recording
CHUNK = 1024  # Size of audio chunk
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate
OUTPUT_FILE = "audio/live_recording.wav"  # Output file

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording... (Press Ctrl+C to stop)")

frames = []

try:
    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        # Save the recording continuously
        with wave.open(OUTPUT_FILE, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

except KeyboardInterrupt:
    print("\nRecording stopped.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the final recording
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {OUTPUT_FILE}.")
