import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def choose_destination():
    destinations = [
        "Switzerland",
        "Japan",
        "Italy",
        "Norway",
        "Iceland",
        "Australia"
    ]
    return destinations[0]

def main():
    destination = choose_destination()
    print("Selected destination:", destination)
    print("Travel video automation started.")

if __name__ == "__main__":
    main()
