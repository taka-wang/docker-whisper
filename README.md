# docker-whisper

A convenient Dockerized solution transcribes media into subtitles using the Whisper model.

## Get Started

```sh
docker build -t asr .
docker run --rm -it --gpus=all -v $(pwd):/tmp1 asr /bin/bash
#docker run -it --rm --gpus '"device=0,1"' -v $(pwd):/app asr

# execute cpp version
whisper-faster /tmp1/lesson1.mp4 --model_dir=/models/ --model="large-v2" --language=en --output_dir=/tmp1/ --output_format=srt --vad_min_silence_duration_ms=1000 --temperature=1

# execute whisper-ctranslate2 version
whisper-ctranslate2 /tmp1/lesson1.mp4 --model_directory /models/faster-whisper-large-v2/ --vad_filter True --vad_min_silence_duration_ms 1000 --beam_size 5 --print_colors True --output_format srt --device cuda --compute_type float16 --language en

# execute python3 version
python3 simple.py -i /tmp1/lesson1.mp4 -o /tmp1/lesson1.srt
```

## Recognition & Translation

```sh
# local file
python3 app.py -i /tmp1/lesson1.mp4

# from YT
python3 app.py -i https://youtu.be/XZEkIK4_d-o -l fr
```

---

## References

- [Faster Whisper transcription with CTranslate2](https://github.com/guillaumekln/faster-whisper/tree/5a0541ea7d054aa3716ac492491de30158c20057)
- [whisper-standalone-win](https://github.com/Purfview/whisper-standalone-win)
- [whisper-ctranslate2](https://github.com/Softcatala/whisper-ctranslate2)
