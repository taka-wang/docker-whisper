# whisper-subtitle

Generate subtitle from multiple mp4 files with whisper

## Get Started

```sh
docker build -t asr .
docker run --rm -it --gpus=all -v $(pwd):/tmp1 asr /bin/bash
#docker run -it --rm --gpus '"device=0,1"' -v $(pwd):/app asr

# cpp version
whisper-faster /tmp1/lesson1.mp4 --model_dir=/models/ --model="large-v2" --language=en --output_dir=/tmp1/ --output_format=srt --vad_min_silence_duration_ms=1000 --temperature=1

# python3 version
python3 app.py -i /tmp1/lesson1.mp4 -o /tmp1/lesson1.srt
```
---

## References

- [](https://github.com/Purfview/whisper-standalone-win)
- [](https://github.com/guillaumekln/faster-whisper/blob/5a0541ea7d054aa3716ac492491de30158c20057/faster_whisper/transcribe.py#L125)
