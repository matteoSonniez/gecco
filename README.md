# Podcast Bot Python (Claude + ElevenLabs v3)

Ce projet genere automatiquement:
1. un script de livre audio podcast ultra naturel (Anthropic Claude),
2. puis l'audio final MP3 (ElevenLabs `eleven_v3`),
3. stocke dans `upload/<Theme>/` a la racine.

## Themes

| Theme | Style voix | Sous-categories | Statut |
|---|---|---|---|
| `savoir` | Posee, claire, documentaire premium | science, histoire, philosophie, economie, politique, geopolitique, droit, religions, culture generale | Actif |
| `humaine` | Douce, empathique, conversationnelle | psychologie, societe, sante, dev perso, education, voyage | Bientot |
| `decouverte` | Expressive, contemplative, captivante | espace, environnement, nature, archeologie, mythologie, mysteres du monde | Actif |
| `tech` | Energique, jeune, fluide, rythmee | technologie, IA, informatique, business, finance, medias | Bientot |
| `culture` | Sophistiquee, expressive, artistique | arts, litterature, musique, cinema, architecture, histoire de l'art | Actif |
| `mystere` | Profonde, tendue, immersive, cinematographique | faits divers, true crime, paranormal, thriller, enquete, suspense | Actif |

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1) Cree un fichier `.env` a partir de `.env.example`
2) Renseigne tes variables:

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_MODEL=claude-sonnet-4-20250514`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_MODEL_ID=eleven_v3`
- `VOIX_SAVOIR=<voice_id>` (une variable par theme)

Chaque `VOIX_*` est prioritaire sur `ELEVENLABS_VOICE_ID`.

## Utilisation

Mode interactif:

```bash
python main.py
```

Le script affiche les themes disponibles puis demande:
- le theme (`savoir`, `decouverte`, `mystere`, `culture`)
- la duree cible (minutes)
- le sous-theme exact
- le style voix (`creative`, `natural`, `robust`)
- le niveau d'energie (`low`, `medium`, `high`)
- le nombre de brouillons (1-5)

Mode ligne de commande:

```bash
python main.py --theme savoir --minutes 6 --subtheme "la gravitation" --voice-style natural --energy medium --draft-count 3 --save-script
python main.py --theme decouverte --minutes 5 --subtheme "les volcans sous-marins" --voice-style natural --energy medium --draft-count 3 --save-script
python main.py --theme mystere --minutes 8 --subtheme "l'affaire Dupont de Ligonnes" --voice-style natural --energy medium --draft-count 3 --save-script
python main.py --theme culture --minutes 6 --subtheme "Guernica de Picasso" --voice-style natural --energy medium --draft-count 3 --save-script
```

Lister les voix ElevenLabs (nom + id):

```bash
python main.py --list-voices
```

Lister les themes:

```bash
python main.py --list-themes
```

Resultat:
- audio: `upload/Savoir/<timestamp>-savoir-<subtheme>.mp3`
- script texte (optionnel): `upload/Savoir/<timestamp>-savoir-<subtheme>.txt`

## Realisme v2 (active par defaut)

- generation en 2 passes (brouillon puis reecriture orale),
- generation de plusieurs brouillons (`--draft-count`) puis choix automatique du meilleur,
- pilotage de la prosodie via `--voice-style`,
- pilotage du ton narratif via `--energy`.
