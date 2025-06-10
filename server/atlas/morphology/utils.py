import unicodedata

from pyuca.collator import Collator


collator = Collator()

def sort_key(s):
    return " ".join(
        str(n).zfill(5)
        for n in collator.sort_key(unicodedata.normalize("NFD", s))
    )


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def parse_sort_key(parse, lang):
    if lang == "grc":
        return parse_sort_key_grc(parse)
    elif lang == "ang":
        return parse_sort_key_ang(parse)
    elif lang == "lat":
        return parse_sort_key_lat(parse)


def parse_sort_key_ang(parse):
    if len(parse) > 2 and parse[1] in "nagd" and parse[2] in "sp":
        case = {
            "n": "1",
            "a": "2",
            "g": "3",
            "d": "4",
        }[parse[1]]
        number = {
            "s": "1",
            "p": "2",
        }[parse[2]]
        return case + number
    else:
        return "0"


def parse_sort_key_grc(parse):
    person = {
        "1": "1",
        "2": "2",
        "3": "3",
        "-": "0",
    }[parse[0]]
    number = {
        "s": "1",
        "d": "2",
        "p": "3",
        "-": "0",
    }[parse[1]]
    tense_voice = {
        "pa": "10",
        "pe": "10",
        "pm": "10",
        "pp": "10",  # @@@
        "p-": "10",  # @@@ @@@
        "ia": "15",
        "ie": "15",
        "im": "15",
        "ip": "15",  # @@@
        "i-": "15",  # @@@ @@@
        "fa": "20",
        "fm": "20",
        "fe": "20",
        "f-": "20",  # @@@
        "aa": "30",
        "am": "30",
        "ae": "30",  # @@@
        "ad": "30",  # @@@
        "a-": "39",  # @@@
        "ra": "40",
        "re": "40",
        "rm": "40",
        "rp": "40",  # @@@
        "r-": "40",  # @@@ @@@
        "la": "45",
        "lm": "45",  # @@@
        "le": "45",
        "lp": "45",  # @@@
        "l-": "45",  # @@@ @@@
        "ap": "60",
        "fp": "70",
        "ta": "80",  # @@@
        "te": "80",  # @@@
        "tm": "80",  # @@@
        "tp": "80",  # @@@
        "t-": "80",  # @@@ @@@
        "-a": "99",  # @@@
        "-e": "99",  # @@@ @@@
        "-m": "99",  # @@@ @@@
        "-p": "99",  # @@@ @@@ @@@
        "--": "00",
    }[parse[2] + parse[4]]
    voice = {
        "a": "1",
        "m": "2",
        "e": "2",
        "p": "3",
        "-": "0",
    }[parse[4]]
    mood = {
        "n": "1",
        "i": "2",
        "m": "3",
        "s": "4",
        "o": "5",
        "p": "6",
        "g": "7",  # @@@ @@@
        "-": "0",
    }[parse[3]]
    gender = {
        "m": "1",
        "f": "2",
        "n": "3",
        "-": "0",
        "c": "9",  # @@@
    }[parse[5]]
    case = {
        "n": "1",
        "a": "2",
        "g": "3",
        "d": "4",
        "v": "5",
        "-": "0",
    }[parse[6]]
    degree = {
        "-": "0",
        "c": "1",
        "s": "2",
    }[parse[7]]

    return tense_voice + mood + voice + degree + gender + number + case + person


def parse_sort_key_lat(parse):
    person = {
        "1": "1",
        "2": "2",
        "3": "3",
        "-": "0",
        "_": "0",  # @@@
    }[parse[0]]
    number = {
        "s": "1",
        "d": "2",
        "p": "3",
        "-": "0",
        "_": "0",  # @@@
    }[parse[1]]
    tense_voice = {
        "pa": "10",
        "pd": "10",
        "pe": "10",
        "pm": "10",
        "pp": "10",  # @@@
        "p-": "10",  # @@@ @@@
        "p_": "10",  # @@@ @@@
        "ia": "15",
        "id": "15",  # @@@
        "ie": "15",
        "im": "15",
        "ip": "15",  # @@@
        "i-": "15",  # @@@ @@@
        "fa": "20",
        "fm": "20",
        "fd": "20",  # @@@
        "fe": "20",
        "f-": "20",  # @@@
        "aa": "30",
        "am": "30",
        "ae": "30",  # @@@
        "ad": "30",  # @@@
        "a-": "39",  # @@@
        "ra": "40",
        "rd": "40",
        "re": "40",
        "rm": "40",
        "rp": "40",  # @@@
        "r-": "40",  # @@@ @@@
        "r_": "40",  # @@@ @@@
        "la": "45",
        "lm": "45",  # @@@
        "le": "45",
        "lp": "45",  # @@@
        "l-": "45",  # @@@ @@@
        "ap": "60",
        "fp": "70",
        "ta": "80",  # @@@
        "te": "80",  # @@@
        "tm": "80",  # @@@
        "tp": "80",  # @@@
        "t-": "80",  # @@@ @@@
        "-a": "99",  # @@@
        "-e": "99",  # @@@ @@@
        "-m": "99",  # @@@ @@@
        "-p": "99",  # @@@ @@@ @@@
        "--": "00",
        "_a": "99",  # @@@
        "_d": "99",  # @@@
        "_p": "99",  # @@@
        "__": "00",  # @@@
    }[parse[2] + parse[4]]
    voice = {
        "a": "1",
        "m": "2",
        "d": "2",
        "e": "2",
        "p": "3",
        "u": "4",  # @@@
        "-": "0",
        "_": "0",  # @@@
    }[parse[4]]
    mood = {
        "n": "1",
        "i": "2",
        "m": "3",
        "s": "4",
        "o": "5",
        "p": "6",
        "g": "7",  # @@@ @@@
        "d": "8",  # @@@ @@@
        "u": "9",  # @@@ @@@
        "-": "0",
        "_": "0",  # @@@
    }[parse[3]]
    gender = {
        "m": "1",
        "f": "2",
        "n": "3",
        "-": "0",
        "_": "0",  # @@@
        "c": "9",  # @@@
    }[parse[5]]
    case = {
        "n": "1",
        "a": "2",
        "g": "3",
        "d": "4",
        "v": "5",
        "b": "6",  # @@@
        "l": "7",  # @@@
        "_": "0",  # @@@
        "-": "0",
    }[parse[6]]
    degree = {
        "_": "0",  # @@@
        "-": "0",
        "p": "0",
        "c": "1",
        "s": "2",
    }[parse[7]]

    return tense_voice + mood + voice + degree + gender + number + case + person


def human_pos(pos, lang):
    if lang == "grc":
        return human_pos_grc(pos)
    elif lang == "ang":
        return human_pos_ang(pos)
    elif lang == "lat":
        return human_pos_lat(pos)


def human_pos_grc(pos):
    return {
        "a-": "ADJ",
        # "ae": "PROP.ADJ",
        "c-": "CONJ",
        "d-": "ADV",
        # "dd": "ADV?",
        # "de": "ADV?",
        # "di": "ADV?",
        # "dr": "ADV?",
        # "dx": "ADV?",
        "g-": "PTCL",
        # "gm": "MODAL.PTCL",
        "i-": "INTJ",
        "l-": "ART",
        "m-": "NUM",
        "n-": "NOUN",
        # "ne": "PROP.NOUN",
        "p-": "PRONOUN",
        # "pa": "PRONOUN?",
        # "pc": "PRONOUN?",
        # "pd": "PRONOUN?",
        # "pi": "PRONOUN?",
        # "pp": "PRONOUN?",
        # "pr": "PRONOUN?",
        # "ps": "PRONOUN?",
        # "px": "PRONOUN?",
        "r-": "PREP",
        "u-": "PUNC",
        "v-": "VERB",
        "vc": "COPULA",
    }.get(pos, pos)


def human_pos_ang(pos):
    return {
        "m": "NOUN.MASC",
        "n": "NOUN.NEUT",
        "f": "NOUN.FEM",
        "v": "VERB",
        "a": "ADJ",
        "av": "ADVERB",
        "np": "PROP.NOUN",
        "p": "PRONOUN",
        "pp": "PREP",
        "c": "CONJ",
        "d": "DET",
        "nu": "NUM",
        "e": "EXCL",
        "r": "REL.PRON",
    }.get(pos, pos)


def human_pos_lat(pos):
    return {
        "a-": "ADJ",
        "c-": "CONJ",
        "d-": "ADV",
        "g-": "PTCL",
        "i-": "INTJ",
        "l-": "ART",
        "m-": "NUM",
        "n-": "NOUN",
        "p-": "PRONOUN",
        "r-": "PREP",
        "u-": "PUNC",
        "v-": "VERB",
    }.get(pos, pos)



def human_parse(parse, lang):
    if lang == "grc":
        return human_parse_grc(parse)
    elif lang == "ang":
        return human_parse_ang(parse)
    elif lang == "lat":
        return human_parse_lat(parse)


def human_parse_ang(parse):
    if len(parse) > 2 and parse[1] in "nagd" and parse[2] in "sp":
        case = {
            "n": "NOM",
            "a": "ACC",
            "g": "GEN",
            "d": "DAT",
        }[parse[1]]
        number = {
            "s": "SG",
            "p": "PL",
        }[parse[2]]
        return case + "." + number
    else:
        return parse


def human_parse_grc(parse):
    if len(parse) == 8:
        if parse == "--------":
            return "INDECL"
        else:
            person = {
                "-": None,
            }.get(parse[0], parse[0])
            number = {
                "s": "SG",
                "d": "DU",
                "p": "PL",
                "-": None,
            }.get(parse[1], parse[1])
            tense = {
                "p": "PRES",
                "i": "IMPRF",
                "f": "FUT",
                "a": "AOR",
                "r": "PRF",
                "l": "PLPRF",
                "-": None,
            }.get(parse[2], parse[2])
            mood = {
                "i": "IND",
                "m": "IMP",
                "n": "INF",
                "s": "SBJV",
                "o": "OPT",
                "p": "PTCP",
                "-": None,
            }.get(parse[3], parse[3])
            voice = {
                "a": "ACT",
                "m": "MID",
                "e": "MID",
                "p": "PASS",
            }.get(parse[4], parse[4])
            gender = {
                "m": "MASC",
                "f": "FEM",
                "n": "NEUT",
                "-": None,
            }.get(parse[5], parse[5])
            case = {
                "n": "NOM",
                "a": "ACC",
                "g": "GEN",
                "d": "DAT",
                "v": "VOC",
                "-": None,
            }.get(parse[6], parse[6])
            degree = {
                "c": "COMP",  # @@@
                "s": "SUP",  # @@@
                "-": None,
            }.get(parse[7], parse[7])
            if case and tense:
                if mood != "PTCP":
                    return f"@1@ {parse}"
                return f"{tense} {voice} {case}.{number} {gender} {mood}"
            elif case and not tense:
                if degree:
                    return f" {degree} {case}.{number} {gender}"
                if gender:
                    return f"{case}.{number} {gender}"
                else:
                    return f"{case}.{number}"
            elif tense and not case:
                if person:
                    return f"{tense} {voice} {person}{number} {mood}"
                elif mood == "INF":
                    return f"{tense} {voice} {mood}"
                else:
                    return f"@@@ {parse}"
            else:
                return f"@@@ {parse}"
    else:
        return "UNKNOWN"


def human_parse_lat(parse):
    if len(parse) == 8:
        if parse == "--------":
            return "INDECL"
        else:
            person = {
                "-": None,
            }.get(parse[0], parse[0])
            number = {
                "s": "SG",
                "d": "DU",
                "p": "PL",
                "-": None,
            }.get(parse[1], parse[1])
            tense = {
                "p": "PRES",
                "i": "IMPRF",
                "f": "FUT",
                "a": "AOR",
                "r": "PRF",
                "l": "PLPRF",
                "-": None,
            }.get(parse[2], parse[2])
            mood = {
                "i": "IND",
                "m": "IMP",
                "n": "INF",
                "s": "SBJV",
                "o": "OPT",
                "p": "PTCP",
                "-": None,
            }.get(parse[3], parse[3])
            voice = {
                "a": "ACT",
                "m": "MID",
                "e": "MID",
                "p": "PASS",
            }.get(parse[4], parse[4])
            gender = {
                "m": "MASC",
                "f": "FEM",
                "n": "NEUT",
                "-": None,
            }.get(parse[5], parse[5])
            case = {
                "n": "NOM",
                "a": "ACC",
                "g": "GEN",
                "d": "DAT",
                "v": "VOC",
                "b": "ABL",  # @@@
                "l": "LOC",  # @@@
                "-": None,
            }.get(parse[6], parse[6])
            degree = {
                "c": "COMP",  # @@@
                "s": "SUP",  # @@@
                "-": None,
            }.get(parse[7], parse[7])
            if case and tense:
                if mood != "PTCP":
                    return f"@1@ {parse}"
                return f"{tense} {voice} {case}.{number} {gender} {mood}"
            elif case and not tense:
                if degree:
                    return f" {degree} {case}.{number} {gender}"
                if gender:
                    return f"{case}.{number} {gender}"
                else:
                    return f"{case}.{number}"
            elif tense and not case:
                if person:
                    return f"{tense} {voice} {person}{number} {mood}"
                elif mood == "INF":
                    return f"{tense} {voice} {mood}"
                else:
                    return f"@@@ {parse}"
            else:
                return f"@@@ {parse}"
    else:
        return "UNKNOWN"

