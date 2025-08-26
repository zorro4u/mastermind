""" Language Package
    --> EN, GER, FRA
"""

# English, standard
EN = {
    'short':    "en",
    # setup
    'lang1':    "Language",
    'rep':      "Characters_unique",
    'dig':      "Digits/(letters)",
    'char':     "Number_characters",
    'col':      "Number_columns",
    'limit':    "Attempt_limit",
    'coder':    "Coder_autom",
    'solver':   "Solver_auto",
    'algo':     "Solver_algo",
    'hint':     "Solution_notes",
    'stat':     "Statistic_run",
    'file':     "file_load",
    'runs':     "Runs",
    'solu':     "Solutions",
    'feedb':    "Answer_combinat.",

    'in1':      "Input to short/long",
    'in2':      "Input not in char set",
    'in3':      "Input without repetitions",
    'only1':    "Only digits possible from",
    'only2':    "Input: 0/1/n/y",
    'loading':  "are loading",
    'storing':  "are storing",
    'done':     "done",
    'nfound':   "not founded",
    'thecode':  "The code was",
    'repeat':   "Repeat the game",
    'setup':    "Setup all right",
    'end':      "End",
    'n/y':      "<n/y>",
    'y/n':      "<y/n>",
    'black':    ["b", "black"],
    'white':    ["w", "white"],
}

# Standard, used as it is
LANG_ALL = {
    'lang2':    "en:1 de:2 fr:3",   # must be extend on new language
    'alg_A':    "Rand:1 Knut:2",
    'alg_B':    "Kooi:3 Irvi:4",
    'algo_all': "Algo_all",
    'secret':   "code",
    'thread':   "Thread_mode",
    'yes':      [],
    'no':       [],
}
EN |= LANG_ALL


# ==========================================================

# German  // (setup cut-off col:38)
GER = {
    'short':    "de",
    # setup
    'lang1':    "Sprache",
    'rep':      "einmalige_Zeichen",
    'dig':      "Ziffern/(Buchst.)",
    'char':     "Anzahl_Zeichen",
    'col':      "Anzahl_Spalten",
    'limit':    "Versuche_max.",
    'coder':    "Kodierer_autom",
    'solver':   "Dekodierer_autom",
    'algo':     "Lösungsalgoritmus",
    'hint':     "Hinweise",
    'stat':     "Statistik_Modus",
    'file':     "Datei_laden",
    'runs':     "Durchläufe",
    'solu':     "Lösungen",
    'feedb':    "Kombinationen_max",

    'in1':      "Eingabe zu kurz/lang",
    'in2':      "Zeichen nicht vorhanden",
    'in3':      "Eingabe ohne Wiederholungen",
    'only1':    "Nur Ziffern möglich von",
    'only2':    "Eingabe: 0/1/n/j",
    'loading':  "wird geladen",
    'storing':  "wird gespeichert",
    'done':     "fertig",
    'nfound':   "nicht gefunden",
    'thecode':  "Der Kode war",
    'repeat':   "Spiel wiederholen",
    'setup':    "Setup in Ordnung",
    'end':      "Ende",
    'n/y':      "<n/j>",
    'y/n':      "<j/n>",
    'yes':      ["j", "ja"],
    'no':       ["n", "nein"],
    'black':    ["s", "schwarz"],
    'white':    ["w", "weiss"],
}

# French
FRA = {
    'short':    "fr",
    # configuration
    'lang1':    "Langue",
    'rep':      "Caractères_uniques",
    'dig':      "Chiffres/(lettres)",
    'char':     "Nombre_caractères",
    'col':      "Nombre_colonnes",
    'limit':    "Essais_maximum",
    'coder':    "Encodeur_autom",
    'solver':   "Décodeur_autom",
    'algo':     "Solution_algo",
    'hint':     "Indications",
    'stat':     "Mode_statistique",
    'file':     "fichier_charg.",
    'runs':     "Passages",
    'solu':     "Solutions",
    'feedb':    "Combinaisons_max",

    'in1':      "Entrée trop courte/longue",
    'in2':      "Caractères inexistants",
    'in3':      "Entrée sans répétitions",
    'only1':    "Chiffres seulement possibles de",
    'only2':    "Entrée:  0/1/n/o",
    'loading':  "est chargé",
    'storing':  "est enregistré",
    'done':     "terminé",
    'nfound':   "non trouvé",
    'thecode':  "Le code était",
    'repeat':   "Répéter le jeu",
    'setup':    "Config. correcte",
    'end':      "fin",
    'n/y':      "<n/o>",
    'y/n':      "<o/n>",
    'yes':      ["o", "oui"],
    'no':       ["n", "non"],
    'black':    ["n", "noir"],
    'white':    ["b", "blanc"],
}
