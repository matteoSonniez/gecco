from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


THEME_SUBCATEGORIES: dict[str, list[str]] = {
    "savoir": [
        "science", "histoire", "philosophie", "economie", "politique",
        "geopolitique", "droit et justice", "religions", "culture generale",
    ],
    "humaine": [
        "psychologie", "societe", "sante", "developpement personnel",
        "education", "voyage et civilisations",
    ],
    "decouverte": [
        "espace", "environnement", "nature et animaux", "archeologie",
        "mythologie", "mysteres du monde",
    ],
    "tech": [
        "technologie", "intelligence artificielle", "informatique",
        "business et entrepreneuriat", "finance", "medias et communication",
    ],
    "culture": [
        "arts et culture", "litterature", "musique", "cinema",
        "architecture", "histoire de l'art",
    ],
    "mystere": [
        "faits divers", "true crime", "mysteres et paranormal",
        "thriller", "enquete", "suspense",
    ],
}


@dataclass(frozen=True)
class ThemeConfig:
    name: str
    voice_env_key: str
    description: str


@dataclass(frozen=True)
class AppConfig:
    anthropic_api_key: str
    anthropic_model: str
    elevenlabs_api_key: str
    elevenlabs_model_id: str
    default_voice_id: str
    upload_dir: Path
    themes: dict[str, ThemeConfig]


def load_config() -> AppConfig:
    load_dotenv()

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514").strip()
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    elevenlabs_model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3").strip()
    default_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
    upload_dir = Path("upload")

    themes = {
        "savoir": ThemeConfig(
            name="savoir",
            voice_env_key="VOIX_SAVOIR",
            description="Posee, claire, documentaire premium",
        ),
        "humaine": ThemeConfig(
            name="humaine",
            voice_env_key="VOIX_HUMAINE",
            description="Douce, empathique, conversationnelle",
        ),
        "decouverte": ThemeConfig(
            name="decouverte",
            voice_env_key="VOIX_DECOUVERTE",
            description="Expressive, contemplative, captivante",
        ),
        "tech": ThemeConfig(
            name="tech",
            voice_env_key="VOIX_TECH",
            description="Energique, jeune, fluide, rythmee",
        ),
        "culture": ThemeConfig(
            name="culture",
            voice_env_key="VOIX_CULTURE",
            description="Sophistiquee, expressive, artistique",
        ),
        "mystere": ThemeConfig(
            name="mystere",
            voice_env_key="VOIX_MYSTERE",
            description="Profonde, tendue, immersive, cinematographique",
        ),
    }

    return AppConfig(
        anthropic_api_key=anthropic_api_key,
        anthropic_model=anthropic_model,
        elevenlabs_api_key=elevenlabs_api_key,
        elevenlabs_model_id=elevenlabs_model_id,
        default_voice_id=default_voice_id,
        upload_dir=upload_dir,
        themes=themes,
    )
