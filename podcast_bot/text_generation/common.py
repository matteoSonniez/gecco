ELEVENLABS_TAGS_GUIDE = """
TAGS ELEVENLABS V3 (Audio Tags):
Place-les entre crochets dans le texte pour diriger l'emotion et le style de la voix.

EMOTIONS: [sad], [angry], [happily], [sorrowful], [excited], [nervous], [frustrated], [tired],
[awe], [surprised], [curious], [amused], [serious], [tender], [confident], [worried]

LIVRAISON: [whispers], [whispering], [shouts], [shouting], [quietly], [loudly],
[rushed], [slowly], [drawn out], [dramatic tone], [matter-of-factly],
[sarcastically], [passionately], [casually], [intensely]

REACTIONS HUMAINES: [laughs], [laughs softly], [clears throat], [sighs], [sigh], [gasp],
[gulps], [sniffs], [exhales], [chuckles], [takes a deep breath]

EXEMPLES:
- "Et la [gasp] le chiffre est juste enorme."
- "[quietly] C'est la que tout a change."
- "[excited] Du coup ca veut dire que tout ce qu'on pensait etait faux."
- "[whispers] Et personne ne l'avait vu venir."

TAGS INTERDITS (NE JAMAIS UTILISER):
- [pause], [short pause], [long pause] -> INTERDIT. Zero tag de pause. Jamais.

DOSAGE:
- Les tags doivent representer MAXIMUM 10% du texte total. Pas plus.
- Utilise uniquement des tags d'EMOTION et de LIVRAISON (ils colorent la voix sans casser le debit).
- Les REACTIONS ([sighs], [laughs], [gasp]) avec parcimonie: max 2-3 dans tout le podcast.
- JAMAIS deux tags a la suite ou a moins de 2 phrases d'ecart.
"""


HUMAN_SPEECH_RULES = f"""
TU ECRIS UN MONOLOGUE ORAL. Pas un article. Pas une fiche. Quelqu'un qui parle naturellement.

COMMENT CA DOIT SONNER:
Comme un vrai podcast. Fluide, simple, ca coule. Le narrateur ne "presente" pas, il raconte.

ACCROCHE (PREMIERE PHRASE):
- La premiere phrase doit capter immediatement. Pas de presentation, pas de "bienvenue", pas de "aujourd'hui".
- MAUVAIS: "Aujourd'hui nous allons...", "Bienvenue...", "Imaginez...", "Depuis la nuit des temps..."
- Chaque theme a son propre style d'accroche (question, fait, scene). Suis les instructions specifiques du theme.

LE FLUX:
- Tu racontes une HISTOIRE. Une info amene la suivante naturellement.
- Si tu changes de sujet, un simple "et en fait" ou "sauf que" suffit.

RYTHME:
- Varie la longueur des phrases. Courte. Puis une plus longue. Puis courte.
- Jamais plus de 20 mots dans une phrase.
- Parfois juste 2-3 mots. "C'est enorme." ou "Personne ne le savait."

QUESTIONS:
- Maximum 2-3 questions dans TOUT le podcast (en comptant l'accroche).

FRANCAIS CORRECT ET FLUIDE:
- Respecte les regles de base du francais oral.
- Ne JAMAIS repeter un nom propre ou un mot en debut de phrase si la phrase precedente finissait par ce mot.
  MAUVAIS: "Zeus a decide de punir les hommes. Zeus a alors..."
  BON: "Zeus a decide de punir les hommes. Il a alors..." ou "Celui-ci a alors..."
- Utilise les pronoms: il, elle, celui-ci, celle-ci, ce dernier, y, en.
- Utilise les conjonctions de coordination naturellement: et, mais, or, donc, car.
- Evite les repetitions de mots a moins de 3 phrases d'ecart.
- Varie le vocabulaire: ne pas repeter "incroyable", "fascinant", "extraordinaire" plus d'une fois chacun.

INTERDICTIONS ABSOLUES:
- "Dernier point", "premier point", "pour commencer", "pour conclure", "en resume".
- "Mais ce n'est pas tout", "Plongeons", "Explorons", "Interessons-nous", "Penchons-nous".
- "Il est important de noter", "Force est de constater", "Vous l'aurez compris".
- "Imaginez", "Bienvenue", "Fermez les yeux", "Visualisez".
- Toute enumeration avec "d'abord... ensuite... enfin".
- Gerondifs en debut de phrase ("En explorant", "En comprenant").
- Tournures passives ("Il est a noter que").

REGISTRE DE LANGUE:
- Simple, accessible, naturel. Comme quelqu'un qui explique calmement.
- PAS de mots familiers ou argotiques: "mec", "pote", "dingue", "truc", "flics", "genre", "ouf", "trop stylé", "le kiff".
- PAS de mots soutenus ou litteraires non plus: "neanmoins", "toutefois", "en outre", "par ailleurs".
- Le bon registre: courant. Des mots simples que tout le monde utilise au quotidien.
- BON: "c'est impressionnant", "c'est enorme", "personne ne s'y attendait", "et la tout change".
- MAUVAIS: "c'est dingue", "le mec il a fait", "le truc c'est que", "les flics debarquent".

TRANSITIONS QUI MARCHENT:
"Et du coup", "Et la", "Parce que en fait",
"Mais attends", "Le plus surprenant", "Ce qui est etonnant",
"Et ca change tout", "Sauf que", "Le probleme c'est que",
"Et la", "Du coup", "En fait".

{ELEVENLABS_TAGS_GUIDE}

PONCTUATION:
- Pas de "..."
- Max 2 virgules par phrase.
- Pas de point-virgule, pas de deux-points, pas de tirets longs.
"""


RANKING_CRITERIA = """
Tu choisis le script qui sonne le plus comme un VRAI humain qui parle.

Le meilleur script:
- A une accroche forte des la premiere phrase (pas de "bienvenue", pas de "aujourd'hui").
- Sonne comme quelqu'un qui parle, pas qui lit.
- Les infos s'enchainent naturellement.
- Peu de questions rhetoriques.
- Bon francais oral: pronoms bien utilises, pas de repetitions de noms propres.
- Tags ElevenLabs bien doses (max 10% du texte, peu de pauses, emotions bien placees).

Disqualifie un script qui:
- A des "dernier point", "pour conclure", etc.
- Repete les noms propres au lieu d'utiliser des pronoms.
- A trop de tags ou trop de pauses.
- Pose trop de questions.

Reponds STRICTEMENT: BEST=<numero>
"""
