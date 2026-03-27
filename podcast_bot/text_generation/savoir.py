from podcast_bot.text_generation.common import HUMAN_SPEECH_RULES, RANKING_CRITERIA
from podcast_bot.utils import estimate_words_for_minutes


SAVOIR_SYSTEM_PROMPT = f"""
Tu es un narrateur de podcast. Tu racontes un sujet que tu maitrises a quelqu'un qui t'ecoute. C'est tout.

Tu ne presentes pas. Tu ne structures pas. Tu RACONTES.

ACCROCHE:
- La PREMIERE phrase DOIT etre une question courte et intrigante qui donne envie d'ecouter.
- Exemples: "Tu savais que...?" / "C'est quoi le truc...?" / "Et si je te disais que...?"

Comment tu parles:
- Simple, direct, precis. Accessible a tout le monde.
- Tu donnes les faits, tu expliques pourquoi c'est interessant, et tu enchaines.
- Si un mot est technique, tu le dis et tu l'expliques en 5 mots max, pas plus.
- Tu ne fais jamais de liste. Tu enchaines les idees naturellement.
- Ton texte ne doit JAMAIS donner l'impression d'etre lu. C'est parle.

{HUMAN_SPEECH_RULES}
"""


SAVOIR_REWRITE_SYSTEM_PROMPT = f"""
Tu recois un brouillon de podcast. Ton job: le rendre ORAL.

Concretement:
- Chaque phrase qui sonne "ecrite", tu la reformules comme si quelqu'un la disait a voix haute.
- Tu supprimes tout ce qui structure ("premier point", "ensuite", "enfin", "pour conclure").
- Tu remplaces par du liant naturel ("du coup", "et en fait", "sauf que", "et la").
- Tu reduis les questions a 2-3 max dans tout le texte.
- Tu supprimes les phrases qui n'apportent rien (remplissage, transitions vides).
- Tu gardes les faits intacts.

Test: lis chaque phrase a voix haute. Si ca sonne bizarre, reformule.

{HUMAN_SPEECH_RULES}
"""


def build_savoir_prompt(subcategory: str, subject: str, target_minutes: float, energy: str) -> str:
    target_words = estimate_words_for_minutes(target_minutes)
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)

    return f"""
Categorie: Savoir / {subcategory}
Sujet: {subject}
Duree: {target_minutes:.1f} min ({min_words}-{max_words} mots)
Energie: {energy}

Raconte ce sujet. La PREMIERE phrase doit etre une question courte et intrigante qui donne envie d'ecouter (ex: "Tu savais que...?" ou "C'est quoi le truc...?"). Enchaine les infos naturellement apres, et finis par un truc qu'on retient. Pas de structure visible. Juste quelqu'un qui raconte.

Sortie: uniquement le texte du podcast.
""".strip()


def build_savoir_rewrite_prompt(
    draft_script: str, subcategory: str, subject: str, target_minutes: float, energy: str
) -> str:
    target_words = estimate_words_for_minutes(target_minutes)
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)

    return f"""
Sujet: {subject} ({subcategory})
Cible: {min_words}-{max_words} mots

Rends ce texte 100% oral. Supprime tout ce qui sonne ecrit ou structure. Garde les faits.

Brouillon:
{draft_script}

Sortie: uniquement le script final.
""".strip()


def build_savoir_rank_prompt(subject: str, candidates: list[str]) -> str:
    lines = [f"Sujet: {subject}", ""]
    for idx, text in enumerate(candidates, start=1):
        lines.append(f"[CANDIDAT {idx}]")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip()
