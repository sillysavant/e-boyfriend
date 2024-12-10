import io
import subprocess

def convert_webm_to_wav(webm_bytes: bytes) -> bytes:
    """
    Converts WEBM audio data to WAV format using ffmpeg.

    Parameters:
        webm_bytes (bytes): Audio file in WEBM format as bytes.

    Returns:
        bytes: Converted WAV file as bytes.
    """
    try:
        # Create an in-memory stream for the input and output
        input_stream = io.BytesIO(webm_bytes)
        output_stream = io.BytesIO()

        # Run ffmpeg command
        process = subprocess.Popen(
            [
                "ffmpeg", "-i", "pipe:0",  # Input from stdin
                "-ar", "16000",            # Resample to 16 kHz
                "-ac", "1",                # Mono channel
                "-f", "wav", "pipe:1"      # Output to stdout
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        wav_data, error = process.communicate(input=input_stream.read())

        if process.returncode != 0:
            raise Exception(f"ffmpeg conversion error: {error.decode()}")

        output_stream.write(wav_data)
        return output_stream.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio conversion failed: {str(e)}"
        )
