#!/bin/bash
# Builds the final launch short from clip.mp4 (animation), vo-v3.mp3 (voice) and captions-v3.ass.
set -e
cd "$(dirname "$0")"
ffmpeg -hide_banner -loglevel error -y -i crew-clip.mp4 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[pp]" -map "[pp]" -an crew-pingpong.mp4
ffmpeg -hide_banner -loglevel error -y -stream_loop 1 -i crew-pingpong.mp4 -i vo-v3.mp3 -filter_complex "[0:v]trim=0:12.8,setpts=PTS-STARTPTS,eq=brightness='if(gte(t,10.75),-0.28,0)':eval=frame,ass=captions-v3.ass,format=yuv420p[v];[1:a]apad,atrim=0:12.8,loudnorm=I=-14:TP=-1.5[a]" -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 19 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 12.8 fullclear-02-launch-crew.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,duration -of compact fullclear-02-launch-crew.mp4
