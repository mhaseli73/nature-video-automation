
import main
import researcher
import script_generator


def run_pipeline():
    print("Starting Travel Video AI Pipeline...")

    print("\n1. Selecting destination...")
    main.main()

    print("\n2. Researching destination...")
    researcher.main()

    print("\n3. Generating video scripts...")
    script_generator.main()

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    run_pipeline()
