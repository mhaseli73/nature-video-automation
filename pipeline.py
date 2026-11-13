import time
import traceback

# Import all pipeline modules
import main
import researcher
import script_generator
import scene_planner
import visual_fetcher
import voiceover_generator

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
    
    # Step 1: Pick a destination
    run_step("Destination Selection", main.main)
    
    # Step 2: Research the destination
    run_step("Destination Research", researcher.main)
    
    # Step 3: Generate the video script
    run_step("Video Script Generation", script_generator.main)
    
    # Step 4: Plan the scenes
    run_step("Scene Planning", scene_planner.main)
    
    # Step 5: Fetch video clips from Pexels
    run_step("Visual Acquisition", visual_fetcher.main)
    
    # Step 6: Generate the voiceover audio
    run_step("Voiceover Generation", voiceover_generator.main)
    
    # Future Step (Uncomment when you build it):
    # run_step("Video Rendering", video_renderer.main)
    
    print("\nPipeline completed successfully!", flush=True)

if __name__ == "__main__":
    run_pipeline()
