import subprocess
import tempfile
from pathlib import Path

import requests

from podcast_bot.config import AppConfig, ThemeConfig


def list_voices(config: AppConfig) -> list[dict[str, str]]:
    if not config.elevenlabs_api_key:
        raise RuntimeError("ELEVENLABS_API_KEY manquant dans l'environnement.")

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": config.elevenlabs_api_key}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code >= 400:
        body = response.text[:500]
        raise RuntimeError(
            f"Echec recuperation voix ElevenLabs ({response.status_code}). Reponse: {body}"
        )

    voices = response.json().get("voices", [])
    result: list[dict[str, str]] = []
    for voice in voices:
        result.append(
            {
                "name": str(voice.get("name", "")).strip(),
                "voice_id": str(voice.get("voice_id", "")).strip(),
                "category": str(voice.get("category", "")).strip(),
            }
        )
    return result


def resolve_voice_id(config: AppConfig, theme: ThemeConfig) -> str:
    from os import getenv

    specific_voice = (getenv(theme.voice_env_key) or "").strip()
    if specific_voice:
        return specific_voice
    if config.default_voice_id:
        return config.default_voice_id
    raise RuntimeError(
        f"Aucune voix configuree: ajoute {theme.voice_env_key} ou ELEVENLABS_VOICE_ID."
    )


_MAX_CHARS = 4500


def _split_text(text: str, max_chars: int = _MAX_CHARS) -> list[str]:
    """Split text into chunks that fit within ElevenLabs character limit.

    Splits on sentence boundaries ('. ') to avoid cutting mid-sentence.
    """
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break

        split_at = remaining.rfind(". ", 0, max_chars)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, max_chars)
        if split_at == -1:
            split_at = max_chars

        chunk = remaining[: split_at + 1].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_at + 1 :].strip()

    return chunks


def _synthesize_chunk(
    url: str,
    headers: dict[str, str],
    payload_base: dict,
    text: str,
    timeout: int = 300,
) -> bytes:
    payload = {**payload_base, "text": text}
    with requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout) as r:
        if r.status_code >= 400:
            body = r.text[:500]
            raise RuntimeError(
                f"Echec ElevenLabs ({r.status_code}). Reponse: {body}"
            )
        audio = b""
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                audio += chunk
    return audio


def synthesize_audio(
    config: AppConfig,
    voice_id: str,
    script_text: str,
    output_path: Path,
    voice_style: str = "natural",
    energy: str = "medium",
) -> Path:
    if not config.elevenlabs_api_key:
        raise RuntimeError("ELEVENLABS_API_KEY manquant dans l'environnement.")

    style_map = {
        "creative": 0.0,
        "natural": 0.5,
        "robust": 1.0,
    }
    style_value_map = {
        "low": 0.15,
        "medium": 0.3,
        "high": 0.45,
    }
    similarity_map = {
        "low": 0.75,
        "medium": 0.8,
        "high": 0.85,
    }

    stability = style_map.get(voice_style, 0.5)
    style_strength = style_value_map.get(energy, 0.3)
    similarity_boost = similarity_map.get(energy, 0.8)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "xi-api-key": config.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload_base = {
        "model_id": config.elevenlabs_model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style_strength,
            "use_speaker_boost": True,
        },
        "output_format": "mp3_44100_128",
    }

    chunks = _split_text(script_text)

    chunks = _split_text(script_text)

    if len(chunks) == 1:
        audio_data = _synthesize_chunk(url, headers, payload_base, chunks[0])
        with output_path.open("wb") as f:
            f.write(audio_data)
    else:
        print(f"  Texte long ({len(script_text)} car.) -> {len(chunks)} parties")
        tmp_files: list[Path] = []
        try:
            for i, text_chunk in enumerate(chunks, start=1):
                print(f"  Synthese partie {i}/{len(chunks)} ({len(text_chunk)} car.)...")
                audio_data = _synthesize_chunk(url, headers, payload_base, text_chunk)
                tmp = Path(tempfile.mktemp(suffix=f"_part{i}.mp3"))
                tmp.write_bytes(audio_data)
                tmp_files.append(tmp)

            concat_list = Path(tempfile.mktemp(suffix=".txt"))
            concat_list.write_text(
                "\n".join(f"file '{f}'" for f in tmp_files),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_list),
                    "-c", "copy", str(output_path),
                ],
                check=True,
                capture_output=True,
            )
        finally:
            for f in tmp_files:
                f.unlink(missing_ok=True)
            if "concat_list" in locals():
                concat_list.unlink(missing_ok=True)

    return output_path
