from fetch_dataset import fetch_dataset
from contextlib import suppress


def main():
    print("Hello from movie-recommendation!")

    with suppress(FileExistsError, KeyboardInterrupt):
        fetch_dataset()


if __name__ == "__main__":
    main()
