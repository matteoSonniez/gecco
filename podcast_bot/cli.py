import argparse
from pathlib import Path

import questionary
from questionary import Style

from podcast_bot.config import THEME_SUBCATEGORIES, load_config
from podcast_bot.elevenlabs_client import list_voices
from podcast_bot.pipeline import IMPLEMENTED_THEMES, run_theme_pipeline

STYLE = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "fg:white bold"),
    ("answer", "fg:green bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green"),
])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generateur de podcast (script GPT + audio ElevenLabs)."
    )
    parser.add_argument("--theme", type=str, help="Theme (ex: savoir, decouverte)")
    parser.add_argument("--subcategory", type=str, help="Sous-categorie (ex: espace)")
    parser.add_argument("--subject", type=str, help="Sujet exact du podcast")
    parser.add_argument("--minutes", type=float, help="Duree cible en minutes")
    parser.add_argument("--save-script", action="store_true", help="Sauvegarder le script texte")
    parser.add_argument("--voice-style", choices=["creative", "natural", "robust"])
    parser.add_argument("--energy", choices=["low", "medium", "high"])
    parser.add_argument("--draft-count", type=int, help="Brouillons (1-5)")
    parser.add_argument("--list-voices", action="store_true", help="Lister les voix ElevenLabs")
    parser.add_argument("--list-themes", action="store_true", help="Lister les themes")
    return parser


def _show_themes() -> None:
    print("\nThemes disponibles:")
    for theme_key, subcats in THEME_SUBCATEGORIES.items():
        active = " [ACTIF]" if theme_key in IMPLEMENTED_THEMES else " [bientot]"
        print(f"  {theme_key}{active}")
        for i, subcat in enumerate(subcats, start=1):
            print(f"    {i}. {subcat}")
    print()


def _interactive_mode() -> dict:
    theme_choices = []
    for key in THEME_SUBCATEGORIES:
        if key in IMPLEMENTED_THEMES:
            theme_choices.append(questionary.Choice(title=f"{key.capitalize()}", value=key))
        else:
            theme_choices.append(
                questionary.Choice(title=f"{key.capitalize()} (bientot)", value=key, disabled="pas encore disponible")
            )

    theme = questionary.select(
        "Theme du podcast:",
        choices=theme_choices,
        style=STYLE,
    ).ask()
    if not theme:
        raise SystemExit("Annule.")

    subcats = THEME_SUBCATEGORIES.get(theme, [])
    subcat_choices = [questionary.Choice(title=s.capitalize(), value=s) for s in subcats]
    subcategory = questionary.select(
        "Sous-categorie:",
        choices=subcat_choices,
        style=STYLE,
    ).ask()
    if not subcategory:
        raise SystemExit("Annule.")

    subject = questionary.text(
        "Sujet exact du podcast:",
        style=STYLE,
    ).ask()
    if not subject or not subject.strip():
        raise SystemExit("Un sujet est requis.")
    subject = subject.strip()

    minutes_str = questionary.select(
        "Duree cible:",
        choices=[
            questionary.Choice(title="2 minutes", value="2"),
            questionary.Choice(title="3 minutes", value="3"),
            questionary.Choice(title="5 minutes", value="5"),
            questionary.Choice(title="7 minutes", value="7"),
            questionary.Choice(title="10 minutes", value="10"),
            questionary.Choice(title="15 minutes", value="15"),
        ],
        style=STYLE,
    ).ask()
    if not minutes_str:
        raise SystemExit("Annule.")

    voice_style = questionary.select(
        "Style voix ElevenLabs:",
        choices=[
            questionary.Choice(title="Creative (libre, expressif)", value="creative"),
            questionary.Choice(title="Natural (equilibre)", value="natural"),
            questionary.Choice(title="Robust (stable, constant)", value="robust"),
        ],
        default="natural",
        style=STYLE,
    ).ask()
    if not voice_style:
        raise SystemExit("Annule.")

    energy = questionary.select(
        "Niveau d'energie:",
        choices=[
            questionary.Choice(title="Low (calme, intime)", value="low"),
            questionary.Choice(title="Medium (equilibre)", value="medium"),
            questionary.Choice(title="High (dynamique)", value="high"),
        ],
        default="medium",
        style=STYLE,
    ).ask()
    if not energy:
        raise SystemExit("Annule.")

    draft_count = questionary.select(
        "Nombre de brouillons (plus = meilleur mais plus long):",
        choices=[
            questionary.Choice(title="1 (rapide)", value="1"),
            questionary.Choice(title="2", value="2"),
            questionary.Choice(title="3 (recommande)", value="3"),
            questionary.Choice(title="5 (maximum)", value="5"),
        ],
        default="3",
        style=STYLE,
    ).ask()
    if not draft_count:
        raise SystemExit("Annule.")

    save_script = questionary.confirm(
        "Sauvegarder le script texte avec l'audio?",
        default=True,
        style=STYLE,
    ).ask()

    return {
        "theme": theme,
        "subcategory": subcategory,
        "subject": subject,
        "minutes": float(minutes_str),
        "voice_style": voice_style,
        "energy": energy,
        "draft_count": int(draft_count),
        "save_script": save_script,
    }


def run_cli() -> None:
    args = build_parser().parse_args()
    config = load_config()

    if args.list_voices:
        voices = list_voices(config)
        if not voices:
            print("Aucune voix trouvee sur ce compte ElevenLabs.")
            return
        print("Voix ElevenLabs disponibles:")
        for voice in voices:
            name = voice.get("name") or "(sans nom)"
            voice_id = voice.get("voice_id") or "(sans id)"
            category = voice.get("category") or "unknown"
            print(f"  {name} [{category}] -> {voice_id}")
        return

    if args.list_themes:
        _show_themes()
        return

    has_cli_args = any([args.theme, args.subcategory, args.subject, args.minutes])

    if has_cli_args:
        theme = (args.theme or "").strip().lower()
        subcategory = (args.subcategory or "").strip()
        subject = (args.subject or "").strip()
        minutes = args.minutes or 5.0
        voice_style = args.voice_style or "natural"
        energy = args.energy or "medium"
        draft_count = args.draft_count or 3
        save_script = args.save_script

        if not theme:
            raise SystemExit("--theme requis en mode CLI.")
        if not subcategory:
            raise SystemExit("--subcategory requis en mode CLI.")
        if not subject:
            raise SystemExit("--subject requis en mode CLI.")
    else:
        params = _interactive_mode()
        theme = params["theme"]
        subcategory = params["subcategory"]
        subject = params["subject"]
        minutes = params["minutes"]
        voice_style = params["voice_style"]
        energy = params["energy"]
        draft_count = params["draft_count"]
        save_script = params["save_script"]

    if draft_count < 1 or draft_count > 5:
        raise SystemExit("draft-count doit etre entre 1 et 5.")

    print(f"\nGeneration du script '{theme}/{subcategory}' sur '{subject}'...")
    output_path, script = run_theme_pipeline(
        config=config,
        theme_name=theme,
        subcategory=subcategory,
        subject=subject,
        target_minutes=minutes,
        voice_style=voice_style,
        energy=energy,
        draft_count=draft_count,
    )
    print("Script genere. Generation audio en cours/terminee.")
    print(f"Audio cree: {output_path}")

    if save_script:
        txt_path = Path(str(output_path).replace(".mp3", ".txt"))
        txt_path.write_text(script, encoding="utf-8")
        print(f"Script texte sauvegarde: {txt_path}")
