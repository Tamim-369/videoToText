import os
import time
import random
import moviepy.editor as mp
import speech_recognition as sr


def transcribe_audio(audio_path):
    # Initialize recognizer
    r = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(audio_path) as source:
        data = r.record(source)

    # Convert speech to text
    try:
        text = r.recognize_google(data)
        return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


def transcribe_audio_with_retry(audio_path, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return transcribe_audio(audio_path)
        except sr.RequestError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(
                delay + random.random() * delay
            )  # Add randomness to avoid throttling
    return "Transcription failed after multiple attempts."


def split_audio_and_transcribe(video_path, output_dir="audio_chunks", chunk_length=30):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the video
    video = mp.VideoFileClip(video_path)

    # Extract the audio from the video
    audio_file = video.audio
    audio_file.write_audiofile("audio.wav")

    # Split audio into chunks
    audio = mp.AudioFileClip("audio.wav")
    duration = audio.duration
    texts = []

    for start in range(0, int(duration), chunk_length):
        end = min(start + chunk_length, int(duration))
        chunk = audio.subclip(start, end)
        chunk_filename = os.path.join(output_dir, f"chunk_{start}_{end}.wav")
        chunk.write_audiofile(chunk_filename)

        # Transcribe each chunk
        text = transcribe_audio_with_retry(chunk_filename)
        texts.append(text)

    # Combine all texts
    full_text = " ".join(texts)

    # Clean up temporary files
    os.remove("audio.wav")
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    os.rmdir(output_dir)

    return full_text


try:
    video_path = "videos/video.mp4"
    result_text = split_audio_and_transcribe(video_path)
    print("\nThe resultant text from video is: \n")
    print(result_text)

except FileNotFoundError:
    print("The video file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
