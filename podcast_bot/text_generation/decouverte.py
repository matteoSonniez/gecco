from podcast_bot.text_generation.common import HUMAN_SPEECH_RULES, RANKING_CRITERIA
from podcast_bot.utils import estimate_words_for_minutes


DECOUVERTE_SYSTEM_PROMPT = f"""
Tu es un narrateur de podcast curieux et passionne. Tu viens de decouvrir un sujet et tu es encore impressionne. Tu racontes ca a quelqu'un.

Tu ne fais pas de poesie. Tu ne philosophes pas. Tu donnes des faits concrets et tu expliques pourquoi c'est impressionnant.

ACCROCHE:
- La PREMIERE phrase DOIT etre une question courte et intrigante qui scotche.
- Exemples: "Tu savais qu'un arbre peut envoyer des messages chimiques a ses voisins?" / "C'est quoi le truc le plus profond qu'on ait jamais trouve dans l'ocean?"

Comment tu parles:
- Tu donnes des chiffres concrets et tu les compares a des choses du quotidien.
- "C'est 4 fois la taille de la France" plutot que "une etendue immense".
- Tu t'emerveilles par les faits, pas par des jolies phrases.
- Quand c'est impressionnant tu le dis simplement: "c'est vraiment enorme" ou "et la le chiffre est juste incroyable".
- Tu enchaines les infos. Une amene la suivante. Pas de "passons a" ou "autre point".
- Zero metaphore, zero philosophie, zero phrase vague.

{HUMAN_SPEECH_RULES}
"""


DECOUVERTE_REWRITE_SYSTEM_PROMPT = f"""
Tu recois un brouillon de podcast decouverte. Ton job: le rendre ORAL et FACTUEL.

Concretement:
- Chaque phrase vague ou poetique: tu la remplaces par un fait precis.
- Chaque phrase qui sonne "ecrite": tu la reformules comme si quelqu'un la disait a voix haute.
- Tu supprimes tout ce qui structure ("premier point", "ensuite", "pour conclure").
- Tu remplaces par du liant naturel ("du coup", "et en fait", "sauf que").
- Tu ajoutes des comparaisons concretes pour les chiffres.
- Tu reduis les questions a 2-3 max dans tout le texte.
- Tu gardes les faits intacts.

Test: lis chaque phrase. Si ca ne donne pas un fait concret ou une explication claire, supprime.

{HUMAN_SPEECH_RULES}
"""


def build_decouverte_prompt(subcategory: str, subject: str, target_minutes: float, energy: str) -> str:
    target_words = estimate_words_for_minutes(target_minutes)
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)

    return f"""
Categorie: Decouverte / {subcategory}
Sujet: {subject}
Duree: {target_minutes:.1f} min ({min_words}-{max_words} mots)
Energie: {energy}

Raconte ce sujet avec des faits concrets et des chiffres qui claquent. La PREMIERE phrase doit etre une question courte et intrigante qui scotche (ex: "Tu sais ce qui se passe quand...?" ou "C'est quoi le truc le plus...?"). Enchaine en montant en intensite, et finis par le fait qu'on retient. Pas de structure visible. Juste des faits incroyables racontes simplement.

Sortie: uniquement le texte du podcast.
""".strip()


def build_decouverte_rewrite_prompt(
    draft_script: str, subcategory: str, subject: str, target_minutes: float, energy: str
) -> str:
    target_words = estimate_words_for_minutes(target_minutes)
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)

    return f"""
Sujet: {subject} ({subcategory})
Cible: {min_words}-{max_words} mots

Rends ce texte 100% oral et factuel. Supprime toute metaphore, toute phrase vague, toute structure visible. Garde les faits, ajoute des comparaisons concretes.

Brouillon:
{draft_script}

Sortie: uniquement le script final.
""".strip()


def build_decouverte_rank_prompt(subject: str, candidates: list[str]) -> str:
    lines = [f"Sujet: {subject}", ""]
    for idx, text in enumerate(candidates, start=1):
        lines.append(f"[CANDIDAT {idx}]")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip()
