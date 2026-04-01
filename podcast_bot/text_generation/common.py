ELEVENLABS_V3_INSTRUCTION = """
Tu generes un script de livre audio podcast en francais pour ElevenLabs v3.

Formate le texte exactement comme un script ElevenLabs v3 professionnel:
- Utilise les balises <break time="Xs" /> pour gerer les pauses et le rythme.
- Utilise les tags d'emotion entre crochets ([solemn], [curious], [tense], [narrative], [warm], etc.) pour diriger le ton de la voix.
- Separe les sections avec ---.
- Le texte doit etre pret a etre envoye directement a l'API ElevenLabs v3.
"""


RANKING_CRITERIA = """
Choisis le meilleur script pour un livre audio podcast ElevenLabs v3.
Celui qui a le meilleur rythme, les meilleures balises break, et les tags d'emotion les mieux places.
Reponds strictement: BEST=<numero>
"""
