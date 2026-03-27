from dataclasses import dataclass
from typing import Callable

from openai import OpenAI
import re

from podcast_bot.config import AppConfig
from podcast_bot.text_generation.common import RANKING_CRITERIA


@dataclass(frozen=True)
class ThemePrompts:
    system_prompt: str
    rewrite_system_prompt: str
    build_prompt: Callable[[str, str, float, str], str]
    build_rewrite_prompt: Callable[[str, str, str, float, str], str]
    build_rank_prompt: Callable[[str, list[str]], str]


def _load_theme_prompts(theme_name: str) -> ThemePrompts:
    if theme_name == "savoir":
        from podcast_bot.text_generation.savoir import (
            SAVOIR_REWRITE_SYSTEM_PROMPT,
            SAVOIR_SYSTEM_PROMPT,
            build_savoir_prompt,
            build_savoir_rank_prompt,
            build_savoir_rewrite_prompt,
        )
        return ThemePrompts(
            system_prompt=SAVOIR_SYSTEM_PROMPT,
            rewrite_system_prompt=SAVOIR_REWRITE_SYSTEM_PROMPT,
            build_prompt=build_savoir_prompt,
            build_rewrite_prompt=build_savoir_rewrite_prompt,
            build_rank_prompt=build_savoir_rank_prompt,
        )

    if theme_name == "decouverte":
        from podcast_bot.text_generation.decouverte import (
            DECOUVERTE_REWRITE_SYSTEM_PROMPT,
            DECOUVERTE_SYSTEM_PROMPT,
            build_decouverte_prompt,
            build_decouverte_rank_prompt,
            build_decouverte_rewrite_prompt,
        )
        return ThemePrompts(
            system_prompt=DECOUVERTE_SYSTEM_PROMPT,
            rewrite_system_prompt=DECOUVERTE_REWRITE_SYSTEM_PROMPT,
            build_prompt=build_decouverte_prompt,
            build_rewrite_prompt=build_decouverte_rewrite_prompt,
            build_rank_prompt=build_decouverte_rank_prompt,
        )

    if theme_name == "mystere":
        from podcast_bot.text_generation.mystere import (
            MYSTERE_REWRITE_SYSTEM_PROMPT,
            MYSTERE_SYSTEM_PROMPT,
            build_mystere_prompt,
            build_mystere_rank_prompt,
            build_mystere_rewrite_prompt,
        )
        return ThemePrompts(
            system_prompt=MYSTERE_SYSTEM_PROMPT,
            rewrite_system_prompt=MYSTERE_REWRITE_SYSTEM_PROMPT,
            build_prompt=build_mystere_prompt,
            build_rewrite_prompt=build_mystere_rewrite_prompt,
            build_rank_prompt=build_mystere_rank_prompt,
        )

    if theme_name == "culture":
        from podcast_bot.text_generation.culture import (
            CULTURE_REWRITE_SYSTEM_PROMPT,
            CULTURE_SYSTEM_PROMPT,
            build_culture_prompt,
            build_culture_rank_prompt,
            build_culture_rewrite_prompt,
        )
        return ThemePrompts(
            system_prompt=CULTURE_SYSTEM_PROMPT,
            rewrite_system_prompt=CULTURE_REWRITE_SYSTEM_PROMPT,
            build_prompt=build_culture_prompt,
            build_rewrite_prompt=build_culture_rewrite_prompt,
            build_rank_prompt=build_culture_rank_prompt,
        )

    raise NotImplementedError(f"Le theme '{theme_name}' n'a pas encore de prompts.")


def _generate_text(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> str:
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = (response.output_text or "").strip()
    if not text:
        raise RuntimeError("OpenAI a retourne une reponse vide.")
    return text


def _sanitize_spoken_labels(script: str) -> str:
    patterns = [
        r"(?im)^\s*(?:\[[^\]]+\]\s*)*(?:mini\s+)?recap(?:\s+simple)?\s*[:\-]\s*",
        r"(?im)^\s*(?:\[[^\]]+\]\s*)*resum[eé]\s*[:\-]\s*",
        r"(?im)^\s*(?:\[[^\]]+\]\s*)*exemple\s+concret\s*[:\-]\s*",
        r"(?im)^\s*(?:\[[^\]]+\]\s*)*conclusion\s*[:\-]\s*",
        r"(?im)^\s*(?:\[[^\]]+\]\s*)*introduction\s*[:\-]\s*",
    ]
    cleaned = script
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _sanitize_tts_flow(script: str) -> str:
    cleaned = script
    cleaned = re.sub(r"\.{3,}", ".", cleaned)
    cleaned = re.sub(r",\s*,+", ", ", cleaned)
    cleaned = re.sub(r"\s*;\s*", ". ", cleaned)
    cleaned = re.sub(r"\s*:\s*", ", ", cleaned)
    cleaned = re.sub(r"\s*[—–]\s*", ", ", cleaned)

    def _trim_extra_commas(match: re.Match[str]) -> str:
        sentence = match.group(0)
        comma_positions = [m.start() for m in re.finditer(r",", sentence)]
        if len(comma_positions) <= 2:
            return sentence
        chars = list(sentence)
        for pos in comma_positions[2:]:
            chars[pos] = " "
        return "".join(chars)

    cleaned = re.sub(r"[^.!?\n]+[.!?]?", _trim_extra_commas, cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _sanitize_ai_patterns(script: str) -> str:
    ai_openers = [
        r"(?i)^Imaginez\b[^.]*\.\s*",
        r"(?i)^Bienvenue\b[^.]*\.\s*",
        r"(?i)^Fermez les yeux\b[^.]*\.\s*",
    ]
    cleaned = script
    for pattern in ai_openers:
        cleaned = re.sub(pattern, "", cleaned)

    ai_transitions = [
        r"(?i)\bMais ce n'est pas tout\b",
        r"(?i)\bPlongeons dans\b",
        r"(?i)\bExplorons\b",
        r"(?i)\bInt[eé]ressons-nous [aà]\b",
        r"(?i)\bIl est temps de\b",
        r"(?i)\bPenchons-nous sur\b",
        r"(?i)\bVous l'aurez compris\b",
        r"(?i)\bComme nous l'avons vu\b",
        r"(?i)\bDans un premier temps\b",
        r"(?i)\bForce est de constater\b",
        r"(?i)\bIl convient de noter\b",
        r"(?i)\bPassons maintenant [aà]\b",
        r"(?i)\bAbordons maintenant\b",
        r"(?i)\bCommen[cç]ons par\b",
        r"(?i)\bDernier point\b",
        r"(?i)\bPremier point\b",
        r"(?i)\bDeuxi[eè]me point\b",
        r"(?i)\bTroisi[eè]me point\b",
        r"(?i)\bPour conclure\b",
        r"(?i)\bPour commencer\b",
        r"(?i)\bEn r[eé]sum[eé]\b",
        r"(?i)\bD'abord\b",
        r"(?i)\bEnsuite\b",
        r"(?i)\bEnfin\b,",
        r"(?i)\bPour finir\b",
        r"(?i)\bIl est [aà] noter\b",
        r"(?i)\bNotons que\b",
        r"(?i)\bSoulignons que\b",
        r"(?i)\bPr[eé]cisons que\b",
    ]
    for pattern in ai_transitions:
        cleaned = re.sub(pattern, "", cleaned)

    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _strip_pause_tags(script: str) -> str:
    return re.sub(r"\[(?:short\s+)?(?:long\s+)?pause\]", "", script, flags=re.IGNORECASE)


def _sanitize(script: str) -> str:
    script = _sanitize_spoken_labels(script)
    script = _sanitize_ai_patterns(script)
    script = _sanitize_tts_flow(script)
    script = _strip_pause_tags(script)
    return script


def generate_script(
    config: AppConfig,
    theme_name: str,
    subcategory: str,
    subject: str,
    target_minutes: float,
    energy: str = "medium",
    draft_count: int = 3,
) -> str:
    if not config.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY manquant dans l'environnement.")

    prompts = _load_theme_prompts(theme_name)
    client = OpenAI(api_key=config.openai_api_key)
    drafts: list[str] = []

    safe_draft_count = max(1, min(draft_count, 5))
    for _ in range(safe_draft_count):
        base_prompt = prompts.build_prompt(subcategory, subject, target_minutes, energy)
        first_pass = _generate_text(
            client=client,
            model=config.openai_model,
            system_prompt=prompts.system_prompt,
            user_prompt=base_prompt,
        )
        rewrite_prompt = prompts.build_rewrite_prompt(
            first_pass, subcategory, subject, target_minutes, energy
        )
        second_pass = _generate_text(
            client=client,
            model=config.openai_model,
            system_prompt=prompts.rewrite_system_prompt,
            user_prompt=rewrite_prompt,
        )
        drafts.append(_sanitize(second_pass))

    judge_prompt = prompts.build_rank_prompt(subject, drafts)
    verdict = _generate_text(
        client=client,
        model=config.openai_model,
        system_prompt=RANKING_CRITERIA,
        user_prompt=judge_prompt,
    )

    match = re.search(r"BEST\s*=\s*(\d+)", verdict, flags=re.IGNORECASE)
    if match:
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(drafts):
            script = drafts[idx]
        else:
            script = drafts[0]
    else:
        script = drafts[0]

    if not script:
        raise RuntimeError("OpenAI a retourne une reponse vide pour le script.")
    return _sanitize(script)
