import base64

def convert_audio_to_base64(file_path):
    with open(file_path, "rb") as audio_file:
        base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
    return base64_audio