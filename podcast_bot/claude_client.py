from dataclasses import dataclass
from typing import Callable

import anthropic
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


def _generate_text(
    client: anthropic.Anthropic,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 16000,
) -> str:
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt.strip(),
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )
    text = ""
    for block in message.content:
        if block.type == "text":
            text += block.text
    text = text.strip()
    if not text:
        raise RuntimeError("Claude a retourne une reponse vide.")
    return text


def generate_script(
    config: AppConfig,
    theme_name: str,
    subcategory: str,
    subject: str,
    target_minutes: float,
    energy: str = "medium",
    draft_count: int = 3,
) -> str:
    if not config.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY manquant dans l'environnement.")

    prompts = _load_theme_prompts(theme_name)
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    drafts: list[str] = []

    safe_draft_count = max(1, min(draft_count, 5))
    for _ in range(safe_draft_count):
        base_prompt = prompts.build_prompt(subcategory, subject, target_minutes, energy)
        first_pass = _generate_text(
            client=client,
            model=config.anthropic_model,
            system_prompt=prompts.system_prompt,
            user_prompt=base_prompt,
        )
        rewrite_prompt = prompts.build_rewrite_prompt(
            first_pass, subcategory, subject, target_minutes, energy
        )
        second_pass = _generate_text(
            client=client,
            model=config.anthropic_model,
            system_prompt=prompts.rewrite_system_prompt,
            user_prompt=rewrite_prompt,
        )
        drafts.append(second_pass)

    if len(drafts) == 1:
        script = drafts[0]
    else:
        judge_prompt = prompts.build_rank_prompt(subject, drafts)
        verdict = _generate_text(
            client=client,
            model=config.anthropic_model,
            system_prompt=RANKING_CRITERIA,
            user_prompt=judge_prompt,
            max_tokens=256,
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
        raise RuntimeError("Claude a retourne une reponse vide pour le script.")
    return script
