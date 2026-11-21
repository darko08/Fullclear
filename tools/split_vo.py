#!/usr/bin/env python3
"""Split one long voiceover into per-sentence mp3s (01.mp3, 02.mp3 ...) for tools/podcast.py.

Saves Runway calls: generate a whole script in 1-2 voice calls, then cut it here.
Alignment: faster-whisper word timestamps matched to the script words (difflib), cut in the silence between sentences.

Usage: python3 tools/split_vo.py <out_dir> <start_index> <voice.mp3> <script.txt>
  script.txt: the exact text sent to the voice model ([tags] allowed; they are ignored).
Prints JSON lines [index, sentence] so they can go into the episode JSON.
"""
import difflib, json, os, re, subprocess, sys
import numpy as np


def norm(w): return re.sub(r'[^a-z0-9]', '', w.lower())


def main():
    out, start, mp3, script = sys.argv[1], int(sys.argv[2]), sys.argv[3], open(sys.argv[4]).read()
    os.makedirs(out, exist_ok=True)
    text = re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', ' ', script)).strip()
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    # merge very short sentences into the previous one (keeps lines readable, avoids 1-word subtitles)
    merged = []
    for s in sents:
        if merged and len(s.split()) <= 3 and len(merged[-1].split()) < 14: merged[-1] += ' ' + s
        else: merged.append(s)
    sents = merged
    sw, owner = [], []
    for i, s in enumerate(sents):
        for w in s.split():
            if norm(w): sw.append(norm(w)); owner.append(i)
    from faster_whisper import WhisperModel
    a = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    segs, _ = WhisperModel('base.en', compute_type='int8').transcribe(np.frombuffer(a, np.float32), word_timestamps=True)
    ww = [w for s in segs for w in s.words]
    wn = [norm(w.word) for w in ww]
    sm = difflib.SequenceMatcher(None, sw, wn, autojunk=False)
    last_end = {}
    first_start = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i = owner[blk.a + k]; w = ww[blk.b + k]
            last_end[i] = max(last_end.get(i, 0), w.end)
            first_start[i] = min(first_start.get(i, 1e9), w.start)
    total = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]))
    # cut only at boundaries that aligned cleanly; otherwise merge the sentence into the next one
    cuts, groups, cur = [0.0], [], [sents[0]]
    for i in range(len(sents) - 1):
        e = last_end.get(i); s2 = first_start.get(i + 1)
        if e is None or s2 is None or s2 < e:
            print(f'note: merged sentence {i + 1} into the next (alignment unclear)', file=sys.stderr)
            cur.append(sents[i + 1]); continue
        cuts.append((e + s2) / 2); groups.append(' '.join(cur)); cur = [sents[i + 1]]
    groups.append(' '.join(cur)); sents = groups
    cuts.append(total)
    lines = []
    for i, s in enumerate(sents):
        n = start + i
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ss', f'{cuts[i]:.3f}', '-to', f'{cuts[i + 1]:.3f}',
                        '-ar', '48000', '-ac', '2', os.path.join(out, f'{n:02d}.mp3')], check=True)
        lines.append([n, s])
    print(json.dumps(lines, ensure_ascii=False))


if __name__ == '__main__':
    main()
