#!/bin/bash

# Transcribe all .mp4 files in /tmp1 directory
for file in /tmp1/*.mp4; do
    # Extract file name without extension
    filename=$(basename -- "$file")
    filename_noext="${filename%.*}"

    # Run whisper-faster command for each file
    whisper-faster "$file" --model_dir=/models/ --model="large-v2" --language=en \
    --output_dir=/tmp1/ --output_format=srt --vad_min_silence_duration_ms=1000 --temperature=1

    echo "Transcription completed for $filename"
done
