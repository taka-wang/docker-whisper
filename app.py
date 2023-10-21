import argparse
import os
from typing import Optional, Tuple
from pathlib import Path
from loguru import logger

from faster_whisper import WhisperModel
import pysubs2
from tqdm import tqdm

from srtranslator import SrtFile
from srtranslator.translators.deepl_scrap import DeeplTranslator
from srtranslator.translators.deepl_api import DeeplApi
from srtranslator.translators.translatepy import TranslatePy

import opencc
import yt_dlp

def setup_argparse():
    # Set up argparse for command line arguments parsing
    parser = argparse.ArgumentParser(description="Transcribe media file and save results in SRT format.")
    parser.add_argument("-i", "--input", required=True, help="Input media file path")
    parser.add_argument("-l", "--lang", default="zh-tw", help="Target language (e.g., 'zh-tw', 'zh', 'fr')")
    return parser.parse_args()

def download(url: str = "https://youtu.be/XZEkIK4_d-o") -> str:
    logger.info('Downloading from the internet..')

    try:
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            filename = Path(f"{info['id']}.wav")
            logger.debug(f"Downloaded: {filename}")
            return f"/tmp/{filename}"

    except yt_dlp.DownloadError as e:
        logger.error(f"Error downloading the video: {e}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


def recognize(input_file: str, lang: Optional[str] = None) -> Tuple[str, str]:
    # speech recognition
    logger.info('Transcribing to subtitle...')

    #model_size = "/models/faster-whisper-medium/"
    model_size = "/models/faster-whisper-large-v2/"

    # Specify the model size and initialize the WhisperModel object
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    # Transcribe audio segments with VAD filtering
    segments, info = model.transcribe(
        input_file,
        language=lang,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

    logger.debug(f"Detected language '{info.language}' with probability {info.language_probability}")

    # Prepare results for SRT file format
    results = []
    timestamps = 0.0  # for progress bar
    with tqdm(total=info.duration, unit=" audio seconds") as pbar:
        for seg in segments:
            segment_dict = {'start': seg.start, 'end': seg.end, 'text': seg.text}
            results.append(segment_dict)
            # Update progress bar based on segment duration
            pbar.update(seg.end - timestamps)
            timestamps = seg.end

        # Handle silence at the end of the audio
        if timestamps < info.duration:
            pbar.update(info.duration - timestamps)

    # Save transcribed segments to SRT file
    subs = pysubs2.load_from_whisper(results)
    output_file = f"{os.path.splitext(input_file)[0]}.srt"
    subs.save(output_file)
    return output_file, info.language

def translate(input_file: str, src_lang: str = 'en', dest_lang: str = 'zh'):
    # translate subtitle
    logger.info(f'Translating subtitle from [{src_lang}] to [{dest_lang}]...')

    should_convert_to_traditional = False
    if dest_lang.lower() in ['zh_tw', 'zh-tw']:
        should_convert_to_traditional = True
        dest_lang = 'zh'

    translator = DeeplTranslator()  # or TranslatePy() or DeeplApi(api_key)
    srt = SrtFile(input_file)
    srt.translate(translator, src_lang, dest_lang)
    srt.wrap_lines()  # Making the result subtitles prettier

    base_filename = os.path.splitext(input_file)[0]
    output_filename = f"{base_filename}.{dest_lang}.srt"
    srt.save(output_filename)
    translator.quit()

    if should_convert_to_traditional:
        zh_tw_filename = f"{base_filename}.zh-tw.srt"
        convert_s2t(output_filename, zh_tw_filename)

def convert_s2t(input_file: str, output_file: str):
    # convert simplified chinese to traditional chinese
    logger.info('Converting Simplified Chinese to Traditional Chinese...')
    converter = opencc.OpenCC('s2twp')  # Use the s2twp.json configuration for Taiwan standard
    with open(input_file, 'r', encoding='utf-8') as f:
        simplified_text = f.read()
        traditional_text = converter.convert(simplified_text)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(traditional_text)

def sanitize_file(file_path):
    # Remove the specified file if it exists
    logger.info("sanitize...")
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.debug(f"{file_path} removed!")


def main():
    # Parse command line arguments
    args = setup_argparse()

    local_file = True

    # Check if the input is a local file or a URL
    if not args.input.startswith("https://"):
        input_file = args.input
    else:
        input_file = download(args.input)
        local_file = False

    # Perform speech recognition
    sub_file, src_lang = recognize(input_file=input_file)

    # Translate the recognized speech to the destination language
    translate(input_file=sub_file, src_lang=src_lang, dest_lang=args.lang)

    # sanitize download file
    if not local_file:
        sanitize_file(input_file)


if __name__ == "__main__":
    main()
