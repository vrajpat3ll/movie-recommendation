from pathlib import Path
import requests
import zipfile

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)

DATASET_LINK = "https://files.grouplens.org/datasets/movielens/ml-32m.zip"

TARGET_DIR = Path("./data")
ZIP_PATH = TARGET_DIR / "ml-32m.zip"
MARKER_FILE = TARGET_DIR / ".FETCHED"

CHUNK_SIZE = (1 << 9) * (1 << 10)  # 512 KB


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TextColumn("ETA"),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task("Downloading", total=total)

            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))


def unzip_file(zip_path: Path, extract_to: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"Corrupted file inside zip: {bad}")
        z.extractall(extract_to)


def fetch_dataset() -> None:
    if TARGET_DIR.exists() and MARKER_FILE.exists():
        print(f"[OK] Dataset already present at {TARGET_DIR.resolve()}")
        return

    if TARGET_DIR.exists():
        print("[ERROR] Target directory exists but unmanaged.")
        raise FileExistsError("Target directory exists but unmanaged.")

    TARGET_DIR.mkdir(parents=True)

    print("[INFO] Downloading dataset...")
    download_file(DATASET_LINK, ZIP_PATH)

    print("[INFO] Extracting...")
    unzip_file(ZIP_PATH, TARGET_DIR)

    ZIP_PATH.unlink()

    MARKER_FILE.write_text(
        f"dataset=movielens-32m\nsource=grouplens\nDowloaded from {DATASET_LINK}"
    )

    print("[DONE] Dataset fetched and locked.")


if __name__ == "__main__":
    fetch_dataset()
