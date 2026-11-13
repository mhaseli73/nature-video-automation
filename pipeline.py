
import time
import traceback

import main
import researcher
import script_generator
import scene_planner


def run_step(name, function):

    print(f"\n{'=' * 50}", flush=True)
    print(f"STARTING: {name}", flush=True)

    start_time = time.time()

    try:
        function()

        elapsed = round(time.time() - start_time, 2)

        print(
            f"COMPLETED: {name} ({elapsed} seconds)",
            flush=True
        )

    except Exception as error:

        print(
            f"FAILED: {name}: {error}",
            flush=True
        )

        traceback.print_exc()

        raise


def run_pipeline():

    print(
        "Starting Travel Video AI Pipeline...",
        flush=True
    )

    run_step(
        "Destination Selection",
        main.main
    )

    run_step(
        "Destination Research",
        researcher.main
    )

    run_step(
        "Video Script Generation",
        script_generator.main
    )

    run_step(
        "Scene Planning",
        scene_planner.main
    )

    print(
        "\nPipeline completed successfully!",
        flush=True
    )


if __name__ == "__main__":
    run_pipeline()
