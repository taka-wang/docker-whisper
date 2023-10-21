import argparse
from faster_whisper import WhisperModel
import pysubs2
from tqdm import tqdm

def recognize(input_file, output_file):
    #model_size = "/models/faster-whisper-medium/"
    model_size = "/models/faster-whisper-large-v2/"

    # Specify the model size and initialize the WhisperModel object
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    # Transcribe audio segments with VAD filtering
    segments, info = model.transcribe(
        input_file,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

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
    subs.save(output_file)

def main():
    parser = argparse.ArgumentParser(description="Transcribe media file and save results in SRT format.")
    parser.add_argument("-i", "--input", help="Input media file path", required=True)
    parser.add_argument("-o", "--output", help="Output subtitle file path", default="output.srt")
    args = parser.parse_args()
    recognize(args.input, args.output)

if __name__ == "__main__":
    main()
