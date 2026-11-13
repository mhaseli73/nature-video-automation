import json
from pathlib import Path
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeAudioClip,
    TextClip, CompositeVideoClip, concatenate_videoclips, vfx
)

def apply_ken_burns(clip, zoom_ratio=0.1):
    """Applies a slow zoom to a video clip to create the Ken Burns effect."""
    def effect(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        new_w, new_h = int(w * (1 + zoom_ratio * t)), int(h * (1 + zoom_ratio * t))
        resized = vfx.resize(frame, newsize=(new_w, new_h))
        # Crop back to original size from the center
        return resized[(new_h-h)//2:(new_h-h)//2 + h, (new_w-w)//2:(new_w-w)//2 + w]
    return clip.fl(effect)

def create_text_overlay(text, duration, fontsize=60, position=('center', 'center')):
    """Creates a simple text overlay with a semi-transparent background."""
    txt_clip = TextClip(
        text, fontsize=fontsize, color='white', font='Arial-Bold',
        stroke_color='black', stroke_width=2, method='caption', size=(1200, None)
    )
    # Add a semi-transparent background for readability
    bg = TextClip(
        text, fontsize=fontsize, font='Arial-Bold', method='caption',
        size=(txt_clip.w + 40, txt_clip.h + 40), color='black'
    ).set_opacity(0.6)
    
    # Combine text and background
    text_with_bg = CompositeVideoClip([bg, txt_clip.set_position('center')])
    return text_with_bg.set_duration(duration).set_position(position)

def main():
    output_dir = Path("output")
    audio_dir = output_dir / "audio"
    
    with open(output_dir / "video_assets.json", encoding="utf-8") as f:
        video_paths = json.load(f)

    audio_files = list(audio_dir.glob("*_narration.mp3"))

    for audio_path in audio_files:
        video_type = audio_path.stem.replace("_narration", "")
        print(f"\nRendering {video_type} video with cinematic effects...")

        narration = AudioFileClip(str(audio_path))
        target_duration = narration.duration

        # --- Build the visual track with Ken Burns effect ---
        clips = []
        current_duration = 0.0
        for path in video_paths:
            if current_duration >= target_duration:
                break
            
            clip = VideoFileClip(path)
            remaining_time = target_duration - current_duration
            
            if clip.duration > remaining_time:
                clip = clip.subclip(0, remaining_time)
            
            # Apply the Ken Burns effect to each clip
            clip = apply_ken_burns(clip, zoom_ratio=0.05)
            clips.append(clip)
            current_duration += clip.duration

        if not clips:
            continue

        visual_track = concatenate_videoclips(clips, method="compose")
        visual_track = visual_track.set_duration(target_duration)

        # --- Add On-Screen Text (Example: Location Title) ---
        # You can pull the actual title from your scene_plan.json
        title_overlay = create_text_overlay(
            "Discover the Hidden Beauty", duration=5, fontsize=80, position=('center', 100)
        )
        # Add the overlay to the visual track
        visual_track = CompositeVideoClip([visual_track, title_overlay])

        # --- Mix Background Music with Narration ---
        # You must place a royalty-free music file in output/bgm.mp3
        bgm_path = output_dir / "bgm.mp3"
        if bgm_path.exists():
            bgm = AudioFileClip(str(bgm_path)).volumex(0.1) # Lower BGM volume to 10%
            bgm = bgm.set_duration(target_duration)
            # Mix narration and BGM
            final_audio = CompositeAudioClip([narration, bgm])
        else:
            print("Warning: No background music found at output/bgm.mp3. Using narration only.")
            final_audio = narration

        final_video = visual_track.set_audio(final_audio)

        # Export the final video
        output_video_path = output_dir / f"{video_type}_final_video.mp4"
        print(f"Exporting to {output_video_path}...")
        final_video.write_videofile(
            str(output_video_path), fps=24, codec="libx264", audio_codec="aac", threads=4, logger="bar"
        )
        
        # Clean up
        final_video.close()
        for c in clips: c.close()
        narration.close()

    print("\nCinematic rendering complete!")

if __name__ == "__main__":
    main()
