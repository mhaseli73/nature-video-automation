import time
import traceback

import main
import researcher
import script_generator
import scene_planner
import visual_fetcher
import voiceover_generator
import video_renderer
import youtube_uploader # <-- NEW IMPORT

def run_step(name, function):
    print(f"\n{'=' * 50}", flush=True)
    print(f"STARTING: {name}", flush=True)
    start_time = time.time()
    try:
        function()
        elapsed = round(time.time() - start_time, 2)
        print(f"COMPLETED: {name} ({elapsed} seconds)", flush=True)
    except Exception as error:
        print(f"FAILED: {name}: {error}", flush=True)
        traceback.print_exc()
        raise

def run_pipeline():
    print("Starting Travel Video AI Pipeline...", flush=True)
    
    run_step("Destination Selection", main.main)
    run_step("Destination Research", researcher.main)
    run_step("Video Script Generation", script_generator.main)
    run_step("Scene Planning", scene_planner.main)
    run_step("Visual Acquisition", visual_fetcher.main)
    run_step("Voiceover Generation", voiceover_generator.main)
    run_step("Video Rendering", video_renderer.main)
    run_step("YouTube Upload", youtube_uploader.main) # <-- NEW STEP
    
    print("\nPipeline completed successfully! Videos are on YouTube.", flush=True)

if __name__ == "__main__":
    run_pipeline()
