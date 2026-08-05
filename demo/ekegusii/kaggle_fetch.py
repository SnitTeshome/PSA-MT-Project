"""Optional convenience: if you keep your own copy of the dictionary/corpora in a
private Kaggle dataset, this fetches it for you instead of a manual download+copy.
Bring-your-own-credential, same discipline as `llm_backends.py` -- your Kaggle
username/key are only ever set as environment variables for this process, never
written to `~/.kaggle/kaggle.json` or anywhere else on disk.
"""

import os
import zipfile
from pathlib import Path


class KaggleFetchError(RuntimeError):
    pass


def fetch_dataset(username, key, dataset_slug, target_dir):
    """Downloads and unzips a Kaggle dataset (`username/dataset-slug` or bare
    `dataset-slug` under your own account) into `target_dir`. Returns the list of
    files present in `target_dir` after extraction, so the caller can check
    whether the file it actually needed showed up."""
    if not username or not key:
        raise KaggleFetchError("Kaggle username and key are both required.")
    if not dataset_slug:
        raise KaggleFetchError("Kaggle dataset identifier (e.g. yourname/your-dataset) is required.")

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    prev_username = os.environ.get("KAGGLE_USERNAME")
    prev_key = os.environ.get("KAGGLE_KEY")
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key
    try:
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
        except ImportError as e:
            raise KaggleFetchError(
                "The `kaggle` package isn't installed -- add it with "
                "`pip install kaggle` (it's in requirements.txt)."
            ) from e

        try:
            api = KaggleApi()
            api.authenticate()
        except Exception as e:
            raise KaggleFetchError(f"Kaggle authentication failed: {e}") from e

        try:
            api.dataset_download_files(dataset_slug, path=str(target_dir), unzip=False)
        except Exception as e:
            raise KaggleFetchError(f"Kaggle download failed for {dataset_slug!r}: {e}") from e
    finally:
        if prev_username is None:
            os.environ.pop("KAGGLE_USERNAME", None)
        else:
            os.environ["KAGGLE_USERNAME"] = prev_username
        if prev_key is None:
            os.environ.pop("KAGGLE_KEY", None)
        else:
            os.environ["KAGGLE_KEY"] = prev_key

    for zip_path in target_dir.glob("*.zip"):
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(target_dir)
        zip_path.unlink()

    return sorted(p.name for p in target_dir.iterdir() if p.is_file())
