import traceback
import sys
from pathlib import Path

print("Starting video editor test", flush=True)

try:
    from modules.video_editor import VideoEditor
    from modules.local_video import LocalVideoGenerator

    print("Getting clips...", flush=True)
    vg = LocalVideoGenerator()
    clips = vg.generate_clips(['tech'], 1)
    print(f"Got {len(clips)} clips", flush=True)

    # Find any existing audio file
    audio_path = None
    for f in Path('outputs').glob('*.wav'):
        audio_path = f
        break

    print(f"Audio: {audio_path}", flush=True)

    if audio_path and clips:
        print("Starting assembly...", flush=True)
        ve = VideoEditor()
        result = ve.assemble(audio_path, [clips[0].path])
        print(f"Result: {result}", flush=True)
        print("SUCCESS!", flush=True)
    else:
        print("Missing audio or clips", flush=True)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    traceback.print_exc(file=sys.stdout)