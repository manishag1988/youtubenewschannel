import traceback
import sys

print("Starting test script", flush=True)

try:
    # Step 1
    print("Step 1: News", flush=True)
    from modules.news_gatherer import NewsGatherer
    stories = NewsGatherer().fetch_all_news()[:2]
    print(f"  Got {len(stories)} stories", flush=True)

    # Step 2
    print("Step 2: Script", flush=True)
    from modules.local_llm import ScriptWriter
    script = ScriptWriter().generate_script(stories, "Test")
    print(f"  Got {script.word_count} words", flush=True)

    # Step 3
    print("Step 3: TTS", flush=True)
    from modules.local_tts import TTSEngine
    audio = TTSEngine().generate(script.full_text[:1000])
    print(f"  Got {round(audio.duration, 1)} seconds", flush=True)

    # Step 4
    print("Step 4: Video", flush=True)
    from modules.local_video import LocalVideoGenerator
    vg = LocalVideoGenerator()
    clips = vg.generate_clips(["tech"], 2)
    print(f"  Got {len(clips)} clips", flush=True)

    print("SUCCESS!", flush=True)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    traceback.print_exc(file=sys.stdout)
    flush=True