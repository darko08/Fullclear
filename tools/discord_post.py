#!/usr/bin/env python3
"""Post a message (optionally with one file) to a Discord channel as the Full Clear bot.
The bot token is injected by the environment proxy (Authorization: Bot proxy-injected); never put a real token here.

Usage: python3 tools/discord_post.py <channel_id> <message.md> [file] [--pin]
Messages longer than 2000 characters are split on blank lines.
"""
import json, subprocess, sys, tempfile

API = 'https://discord.com/api/v10'


def post(ch, text, file=None):
    payload = json.dumps({'content': text, 'allowed_mentions': {'parse': []}, 'flags': 4})  # 4 = suppress link embeds
    cmd = ['curl', '-s', '-X', 'POST', '-H', 'Authorization: Bot proxy-injected', f'{API}/channels/{ch}/messages']
    if file:
        tf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); tf.write(payload); tf.close()
        cmd += ['-F', f'payload_json=<{tf.name};type=application/json', '-F', f'files[0]=@{file}']  # file avoids ';' parsing issues
    else:
        cmd += ['-H', 'Content-Type: application/json', '-d', payload]
    r = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout or '{}')
    if 'id' not in r: raise SystemExit(f'Discord error: {r}')
    return r['id']


def main():
    ch, md = sys.argv[1], open(sys.argv[2]).read().strip()
    file = next((a for a in sys.argv[3:] if not a.startswith('--')), None)
    parts, cur = [], ''
    for block in md.split('\n\n'):
        if len(cur) + len(block) + 2 > 1900: parts.append(cur); cur = block
        else: cur = (cur + '\n\n' + block).strip()
    parts.append(cur)
    ids = [post(ch, t, file if i == len(parts) - 1 else None) for i, t in enumerate(parts)]
    if '--pin' in sys.argv:
        subprocess.run(['curl', '-s', '-X', 'PUT', '-H', 'Authorization: Bot proxy-injected', f'{API}/channels/{ch}/pins/{ids[0]}'], capture_output=True)
    print('posted', ids)


if __name__ == '__main__':
    main()
