from podcast_bot.text_generation.common import ELEVENLABS_V3_INSTRUCTION
from podcast_bot.utils import estimate_words_for_minutes


CULTURE_SYSTEM_PROMPT = f"""
{ELEVENLABS_V3_INSTRUCTION}

Theme: CULTURE. Le podcast parle d'art, litterature, musique, cinema, architecture ou histoire de l'art avec passion et accessibilite.
"""

CULTURE_REWRITE_SYSTEM_PROMPT = f"""
{ELEVENLABS_V3_INSTRUCTION}

Reecris ce brouillon pour en faire un meilleur texte de livre audio podcast sur le theme CULTURE. Garde tous les faits, dates et noms intacts.
"""


def build_culture_prompt(subcategory: str, subject: str, target_minutes: float, energy: str) -> str:
    target_words = estimate_words_for_minutes(target_minutes)
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)

    return f"""
Genere un texte de livre audio podcast pour ElevenLabs v3.

Theme: Culture / {subcategory}
Sujet: {subject}
Longueur: {min_words}-{max_words} mots
Energie: {energy}

Sortie: uniquement le texte brut du podcast.
""".strip()


def build_culture_rewrite_prompt(
    draft_script: str, subcategory: str, subject: str, target_minutes: float, energy: str
) -> str:
    target_words = estimate_words_for_minutes(target_minutes)
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)

    return f"""
Reecris ce brouillon en un texte de livre audio podcast pour ElevenLabs v3.

Sujet: {subject} ({subcategory})
Longueur: {min_words}-{max_words} mots

Brouillon:
{draft_script}

Sortie: uniquement le texte brut du podcast.
""".strip()


def build_culture_rank_prompt(subject: str, candidates: list[str]) -> str:
    lines = [f"Sujet: {subject}", ""]
    for idx, text in enumerate(candidates, start=1):
        lines.append(f"[CANDIDAT {idx}]")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip()
