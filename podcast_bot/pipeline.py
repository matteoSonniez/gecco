from pathlib import Path

from podcast_bot.config import AppConfig
from podcast_bot.elevenlabs_client import resolve_voice_id, synthesize_audio
from podcast_bot.openai_client import generate_script
from podcast_bot.utils import output_audio_path

IMPLEMENTED_THEMES = {"savoir", "decouverte", "mystere", "culture"}


def run_theme_pipeline(
    config: AppConfig,
    theme_name: str,
    subcategory: str,
    subject: str,
    target_minutes: float,
    voice_style: str = "natural",
    energy: str = "medium",
    draft_count: int = 3,
) -> tuple[Path, str]:
    if theme_name not in config.themes:
        available = ", ".join(sorted(config.themes.keys()))
        raise ValueError(f"Theme inconnu '{theme_name}'. Themes dispo: {available}")

    if theme_name not in IMPLEMENTED_THEMES:
        raise NotImplementedError(
            f"Le theme '{theme_name}' est prevu mais pas encore implemente. "
            f"Themes actifs: {', '.join(sorted(IMPLEMENTED_THEMES))}"
        )

    theme = config.themes[theme_name]

    script = generate_script(
        config=config,
        theme_name=theme_name,
        subcategory=subcategory,
        subject=subject,
        target_minutes=target_minutes,
        energy=energy,
        draft_count=draft_count,
    )

    voice_id = resolve_voice_id(config, theme)
    output_path = output_audio_path(config.upload_dir, theme_name, subcategory, subject)
    synthesize_audio(
        config=config,
        voice_id=voice_id,
        script_text=script,
        output_path=output_path,
        voice_style=voice_style,
        energy=energy,
    )
    return output_path, script
