from datetime import datetime
import re
from pathlib import Path


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "podcast"


def estimate_words_for_minutes(minutes: float) -> int:
    # Un debit naturel pour podcast narratif est autour de 145-160 mots/min.
    return max(120, int(minutes * 150))


def output_audio_path(
    upload_dir: Path, theme: str, subcategory: str, subject: str
) -> Path:
    theme_dir = upload_dir / theme.strip().capitalize()
    subcat_dir = theme_dir / subcategory.strip().capitalize()
    subcat_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{ts}-{slugify(subject)}.mp3"
    return subcat_dir / filename
