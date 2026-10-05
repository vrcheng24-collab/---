# Karplus-Strong plucked string: the single tuning note ALPHA plays before the song.
import wave, struct, random
sr, dur, freq = 48000, 3.0, 196.0  # G3
random.seed(7)
n = int(sr / freq)
buf = [random.uniform(-1, 1) for _ in range(n)]
out = []
for i in range(int(sr * dur)):
    v = buf[i % n]
    nxt = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.996
    buf[i % n] = nxt
    out.append(v)
peak = max(abs(x) for x in out)
with wave.open('pluck.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(b''.join(struct.pack('<hh', int(x / peak * 0.5 * 32767), int(x / peak * 0.5 * 32767)) for x in out))
