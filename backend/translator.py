import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

DICTIONARY_ENTRY_SPAN_LIMIT = 500
ITALIAN_DETECTION_THRESHOLD = 0.2
WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žÞþÐð'’‘`]+|[^\sA-Za-zÀ-ÖØ-öø-ÿĀ-žÞþÐð'’‘`]+")

ENGLISH_CONTRACTION_MAP = {
    "isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "don't": "do not", "doesn't": "does not", "didn't": "did not", "can't": "cannot",
    "won't": "will not", "i'm": "i am", "you're": "you are", "we're": "we are",
    "they're": "they are", "it's": "it is", "that's": "that is", "there's": "there is",
    "i've": "i have", "you've": "you have", "we've": "we have", "they've": "they have",
    "i'll": "i will", "you'll": "you will", "we'll": "we will", "they'll": "they will"
}

ITALIAN_TO_ENGLISH = {
    "io": "i", "tu": "you", "lui": "he", "lei": "she", "noi": "we", "voi": "you all", "loro": "they",
    "mi": "me", "me": "me", "ti": "you", "ci": "us", "vi": "you all",
    "mio": "my", "mia": "my", "miei": "my", "mie": "my", "tuo": "your", "tua": "your", "tuoi": "your", "tue": "your",
    "suo": "his", "sua": "her", "suoi": "their", "sue": "their", "nostro": "our", "nostra": "our",
    "il": "the", "lo": "the", "la": "the", "i": "the", "gli": "the", "le": "the", "un": "a", "una": "a", "uno": "a",
    "e": "and", "o": "or", "ma": "but", "se": "if", "non": "not", "si": "yes", "no": "no",
    "ciao": "hello", "salve": "hello", "grazie": "thank you", "per": "for", "favore": "please",
    "acqua": "water", "fuoco": "fire", "aria": "air", "terra": "earth", "amore": "love", "pace": "peace",
    "guerra": "war", "luce": "light", "ombra": "shadow", "drago": "dragon", "magia": "magic",
    "essere": "be", "sono": "am", "sei": "are", "è": "is", "siamo": "are", "siete": "are",
    "avere": "have", "ho": "have", "hai": "have", "ha": "has", "abbiamo": "have", "hanno": "have",
    "andare": "go", "vado": "go", "vai": "go", "va": "go", "venire": "come", "vengo": "come",
    "fare": "do", "faccio": "do", "fa": "does", "dire": "say", "dico": "say", "parlare": "speak",
    "parlo": "speak", "parli": "speak", "parla": "speaks", "vedere": "see", "vedo": "see",
    "chi": "who", "cosa": "what", "dove": "where", "quando": "when", "come": "how", "perché": "why"
}

EXTENDED_ITALIAN_TO_ENGLISH = {
    "domani": "tomorrow", "oggi": "today", "ieri": "yesterday", "adesso": "now",
    "matematica": "math", "test": "test", "esame": "exam", "scuola": "school", "classe": "class",
    "insegnante": "teacher", "studente": "student", "studio": "study", "imparo": "learn",
    "libro": "book", "penna": "pen", "carta": "paper", "computer": "computer", "telefono": "phone",
    "internet": "internet", "programma": "program", "progetto": "project", "codice": "code",
    "errore": "error", "soluzione": "solution", "sistema": "system", "dati": "data",
    "numero": "number", "tempo": "time", "giorno": "day", "notte": "night",
    "casa": "house", "città": "city", "strada": "road", "mondo": "world",
    "uomo": "man", "donna": "woman", "maschio": "male", "femmina": "female",
    "ragazzo": "boy", "ragazza": "girl", "bambino": "child", "famiglia": "family",
    "padre": "father", "madre": "mother", "fratello": "brother", "sorella": "sister",
    "amico": "friend", "nemico": "enemy", "re": "king", "regina": "queen",
    "forza": "strength", "potere": "power", "sapere": "knowledge", "verità": "truth",
    "ordine": "order", "caos": "chaos", "vita": "life", "morte": "death",
    "felice": "happy", "triste": "sad", "forte": "strong", "debole": "weak",
    "grande": "big", "piccolo": "small", "veloce": "fast", "lento": "slow",
    "caldo": "hot", "freddo": "cold", "alto": "high", "basso": "low",
    "vicino": "near", "lontano": "far", "destra": "right", "sinistra": "left",
    "aprire": "open", "apro": "open", "chiudere": "close", "chiudo": "close",
    "iniziare": "start", "inizio": "start", "finire": "finish", "finisco": "finish",
    "correre": "run", "corro": "run", "camminare": "walk", "cammino": "walk",
    "leggere": "read", "leggo": "read", "scrivere": "write", "scrivo": "write",
    "pensare": "think", "penso": "think", "creare": "create", "creo": "create",
    "costruire": "build", "costruisco": "build", "usare": "use", "uso": "use",
    "provare": "test", "provo": "test", "controllare": "check", "controllo": "check"
}

ESSENTIAL_ANCIENT_ADDITIONS = {
    "and": "ok", "or": "eða", "but": "en", "if": "ef", "then": "þá", "because": "því",
    "the": "sá", "is": "er", "are": "eru", "am": "em", "was": "var", "were": "váru",
    "be": "vera", "being": "verandi", "been": "verit", "not": "néiat", "yes": "já", "no": "nei",
    "to": "at", "of": "af", "in": "í", "on": "á", "with": "með", "for": "fyrir", "from": "frá",
    "into": "inn í", "out": "út", "under": "undir", "over": "yfir", "before": "fyrir", "after": "eptir",
    "have": "hafa", "has": "hefir", "had": "hafði", "do": "gera", "does": "gerir", "did": "gerði",
    "can": "mátt", "cannot": "né mátt", "could": "mátti", "will": "mun", "would": "myndi", "should": "skyldi",
    "must": "skal", "may": "megi", "make": "gera", "go": "ganga", "come": "koma", "see": "sjá",
    "know": "kenna", "say": "segja", "speak": "mæla", "think": "hugsa", "want": "vilja", "need": "þurfa",
    "give": "gefa", "take": "taka", "find": "finna", "tell": "segja", "ask": "spyrja",
    "who": "hver", "what": "hvat", "where": "hvar", "when": "hvenær", "why": "hví", "how": "hvernig",
    "all": "allr", "some": "sumr", "many": "margir", "more": "meira", "most": "mest", "few": "fáir",
    "very": "mjök", "much": "mikit", "little": "lítit", "good": "góðr", "bad": "illr",
    "true": "sannr", "new": "nýr", "old": "forn", "first": "fyrstr", "last": "síðastr",
    "today": "í dag", "tomorrow": "á morgin", "yesterday": "í gær", "now": "nú", "always": "æ", "never": "aldri",
    "please": "blítt", "hello": "heill", "thanks": "þakkir", "thank": "þakka"
}

EXTENDED_ESSENTIAL_ANCIENT_ADDITIONS = {
    "a": "einn", "an": "einn", "this": "þessi", "that": "sá", "these": "þessir", "those": "þeir",
    "i": "ek", "you": "þú", "he": "hann", "she": "hún", "it": "þat", "we": "vér", "they": "þeir",
    "my": "mín", "your": "þín", "our": "vár", "their": "þeirra", "his": "hans", "her": "hennar",
    "me": "mik", "him": "hann", "us": "oss", "them": "þá",
    "at": "at", "by": "við", "about": "um", "through": "gegnum", "between": "milli", "against": "gegn",
    "during": "um", "without": "án", "within": "innan", "around": "kring", "above": "yfir", "below": "undir",
    "up": "upp", "down": "niðr", "left": "vinstri", "right": "hægri", "near": "nær", "far": "fjarri",
    "again": "aptr", "soon": "brátt", "late": "seint", "early": "árla", "already": "þegar", "still": "enn",
    "today": "í dag", "tonight": "í nótt", "morning": "morginn", "evening": "kveld", "day": "dagr", "night": "nótt",
    "time": "tími", "year": "ár", "month": "mánuðr", "week": "vika", "hour": "stund", "minute": "mínúta",
    "man": "maðr", "woman": "kona", "male": "karl", "female": "kvenna",
    "boy": "drengr", "girl": "mær", "child": "barn", "children": "börn",
    "person": "maðr", "people": "fólk", "friend": "vinr", "enemy": "óvinr",
    "family": "ætt", "father": "faðir", "mother": "móðir", "brother": "bróðir", "sister": "systir",
    "king": "konungr", "queen": "drottning", "warrior": "drengr", "mage": "galdramaðr",
    "house": "hús", "home": "heimr", "city": "borg", "village": "þorp", "road": "vegr", "world": "heimr",
    "land": "land", "sea": "sær", "sky": "himinn", "sun": "sól", "moon": "máni", "star": "stjarna",
    "stone": "steinn", "metal": "járn", "wood": "viðr", "blood": "blóð", "heart": "hjarta", "mind": "hugr",
    "truth": "sannleikr", "lie": "lygi", "law": "lög", "order": "skipan", "chaos": "óskipan",
    "life": "líf", "death": "dauði", "strength": "afl", "power": "máttr", "magic": "galdr", "knowledge": "vísdómr",
    "work": "verk", "job": "starf", "task": "verk", "problem": "vandi", "solution": "lausn",
    "question": "spurning", "answer": "svar", "idea": "hugmynd", "story": "saga", "name": "nafn",
    "language": "tunga", "word": "orð", "sentence": "setning", "book": "bók", "letter": "stafr",
    "number": "tala", "math": "reikningr", "mathematics": "reikningr", "science": "vísindi",
    "school": "skóli", "class": "bekkr", "teacher": "kennari", "student": "nemi",
    "study": "nema", "learn": "nema", "teach": "kenna", "read": "lesa", "write": "rita",
    "code": "kóði", "program": "forrit", "project": "verk", "system": "kerfi", "data": "gögn",
    "network": "net", "computer": "tölva", "phone": "sími", "internet": "net", "message": "boð",
    "open": "opna", "close": "lúka", "start": "hefja", "finish": "ljúka", "begin": "hefja", "end": "endi",
    "build": "smíða", "create": "skapa", "use": "nota", "check": "kanna", "test": "próf", "exam": "próf",
    "run": "renna", "walk": "ganga", "stop": "stöðva", "turn": "snúa", "move": "hreyfa",
    "bring": "færa", "send": "senda", "receive": "taka", "help": "hjálpa", "protect": "verja",
    "attack": "ráðast", "win": "sigra", "lose": "tapa", "save": "bjarga",
    "hot": "heitr", "cold": "kaldr", "big": "stórr", "small": "lítill", "long": "langr", "short": "stuttr",
    "young": "ungr", "happy": "glaðr", "sad": "sorgmæddr", "strong": "sterkr", "weak": "veikr",
    "easy": "auðveldr", "hard": "erfiðr", "important": "mikilvægr", "different": "ólíkr",
    "same": "sami", "free": "frjáls", "safe": "öruggr", "ready": "búinn",
    "one": "einn", "two": "tveir", "three": "þrír", "four": "fjórir", "five": "fimm",
    "six": "sex", "seven": "sjau", "eight": "átta", "nine": "níu", "ten": "tíu"
}

CANONICAL_BOOK_PHRASES = {
    "let it be": "atra",
    "may good fortune rule over you": "atra esterní ono thelduin",
    "peace live in your heart": "mor'ranr lífa unin hjarta onr",
    "the stars watch over you": "du evarínya ono varda",
    "and the stars watch over you": "un du evarínya ono varda",
}

ALL_ITALIAN_TO_ENGLISH = {**ITALIAN_TO_ENGLISH, **EXTENDED_ITALIAN_TO_ENGLISH}
ALL_ESSENTIAL_ANCIENT_ADDITIONS = {
    **ESSENTIAL_ANCIENT_ADDITIONS,
    **EXTENDED_ESSENTIAL_ANCIENT_ADDITIONS,
    **CANONICAL_BOOK_PHRASES,
}
ANCIENT_TO_ENGLISH_ADDITIONS = {
    "kverst": "strength",
    "malmr": "metal",
    "du": "you",
    "huildrs": "shield maiden",
    "edtha": "and",
    "mar": "many",
    "frëma": "fear",
    "né": "not",
    "thön": "those",
    "eka": "i",
    "threyja": "three",
}
IRREGULAR_ITALIAN_GERUNDS = {
    "facendo": "fare",
    "dicendo": "dire",
    "bevendo": "bere",
    "ponendo": "porre",
    "traendo": "trarre"
}
GLOSS_STRING_KEYS = {"related_words", "components", "example_phrases", "example", "base_example", "compounds"}
ANCIENT_VARIANT_KEYS = ("ancient_language", "formal", "informal", "poetic", "archaic")
VERB_FORM_KEYS = ("present", "past", "future", "subjunctive", "imperative", "participles")


def normalize_apostrophes(text: str) -> str:
    return re.sub(r"[’‘`ʼ]", "'", text)


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def normalize_term(text: str) -> str:
    text = normalize_apostrophes(text.lower())
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[“”\"!?.:]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_english_variants(english: str) -> List[str]:
    normalized = normalize_apostrophes(english.lower())
    normalized = re.sub(r"\([^)]*\)", " ", normalized)
    normalized = re.sub(r"[“”\"!?.:]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return []
    variants = [s.strip() for s in re.split(r",|\s+or\s+|\s*/\s*|;", normalized) if s.strip()]
    expanded: List[str] = []
    for variant in variants:
        expanded.append(variant)
        if variant.startswith("to ") and len(variant) > 3:
            expanded.append(variant[3:].strip())
    return list(dict.fromkeys(expanded))


def add_essential_entries(dictionary: Dict[str, str]) -> None:
    for english, ancient in ALL_ESSENTIAL_ANCIENT_ADDITIONS.items():
        dictionary.setdefault(english, ancient)


def add_normalized_entry(dictionary: Dict[str, str], english: str, ancient: str) -> None:
    normalized_ancient = normalize_term(ancient)
    if not normalized_ancient:
        return
    for variant in split_english_variants(english):
        dictionary.setdefault(variant, normalized_ancient)


def add_gloss_entries_from_structured_vocabulary(raw: str, dictionary: Dict[str, str]) -> None:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return

    def visit(value, parent_key: str = "") -> None:
        if isinstance(value, list):
            for item in value:
                visit(item, parent_key)
            return

        if isinstance(value, dict):
            infinitive = value.get("infinitive")
            translation = value.get("translation")
            if isinstance(infinitive, str) and isinstance(translation, str):
                add_normalized_entry(dictionary, translation, infinitive)
            for key, child in value.items():
                visit(child, key)
            return

        if isinstance(value, str) and parent_key in GLOSS_STRING_KEYS:
            match = re.fullmatch(r"\s*([^()]+?)\s*\(([^()]+)\)\s*", value)
            if match:
                add_normalized_entry(dictionary, match.group(2), match.group(1))

    visit(parsed)


def build_dictionary_from_raw_vocabulary(raw: str) -> Dict[str, str]:
    dictionary: Dict[str, str] = {}
    pair_pattern = re.compile(
        rf'"english"\s*:\s*"([^"]+)"[\s\S]{{0,{DICTIONARY_ENTRY_SPAN_LIMIT}}}?"ancient_language"\s*:\s*"([^"]+)"'
    )
    reverse_pattern = re.compile(r'"word"\s*:\s*"([^"]+)"\s*,\s*"translation"\s*:\s*"([^"]+)"')

    for english, ancient in pair_pattern.findall(raw):
        for variant in split_english_variants(english):
            dictionary.setdefault(variant, ancient)

    for ancient_word, english in reverse_pattern.findall(raw):
        normalized_ancient = normalize_term(ancient_word)
        for variant in split_english_variants(english):
            if normalized_ancient:
                dictionary.setdefault(variant, normalized_ancient)

    add_gloss_entries_from_structured_vocabulary(raw, dictionary)
    add_essential_entries(dictionary)
    return dictionary


def detect_likely_italian(text: str) -> bool:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žÞþÐð']+", normalize_apostrophes(text.lower()))
    if not words:
        return False
    italian_hits = sum(1 for word in words if word in ALL_ITALIAN_TO_ENGLISH)
    return (italian_hits / len(words)) >= ITALIAN_DETECTION_THRESHOLD


def expand_english_contractions(text: str) -> str:
    text = normalize_apostrophes(text)

    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        return ENGLISH_CONTRACTION_MAP.get(token.lower(), token)

    return re.sub(r"\b[A-Za-zÀ-ÖØ-öø-ÿĀ-žÞþÐð']+\b", replace_token, text)


def tokenize(text: str) -> List[str]:
    return WORD_RE.findall(text)


def is_word(token: str) -> bool:
    return bool(re.search(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žÞþÐð']", token))


def rejoin_tokens(tokens: List[str]) -> str:
    no_leading_space = {",", ".", "!", "?", ";", ":", ")", "]", "}"}
    no_trailing_space = {"(", "[", "{"}
    out = []
    for i, token in enumerate(tokens):
        if i == 0 or token in no_leading_space or tokens[i - 1] in no_trailing_space:
            out.append(token)
        else:
            out.append(" " + token)
    return "".join(out)


def english_ing_candidates(word: str) -> List[str]:
    lower = word.lower()
    if not lower.endswith("ing") or len(lower) <= 4:
        return []
    stem = lower[:-3]
    candidates = [stem]
    if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
        candidates.append(stem[:-1])
    if stem and stem[-1] not in "aeiou":
        candidates.append(f"{stem}e")
    # Preserve order and uniqueness.
    return list(dict.fromkeys([candidate for candidate in candidates if candidate]))


def italian_gerund_candidates(word: str) -> List[str]:
    lower = word.lower()
    if len(lower) <= 5:
        return []
    if lower in IRREGULAR_ITALIAN_GERUNDS:
        return [IRREGULAR_ITALIAN_GERUNDS[lower]]
    candidates: List[str] = []
    if lower.endswith("ando"):
        root = lower[:-4]
        candidates.extend([f"{root}are", f"{root}ere", f"{root}ire"])
    if lower.endswith("endo"):
        root = lower[:-4]
        candidates.extend([f"{root}are", f"{root}ere", f"{root}ire"])
    return list(dict.fromkeys([candidate for candidate in candidates if len(candidate) > 2]))


def english_plural_candidates(word: str) -> List[str]:
    lower = word.lower()
    if len(lower) <= 3 or not lower.endswith("s"):
        return []

    candidates: List[str] = []
    if lower.endswith("ies") and len(lower) > 4:
        candidates.append(f"{lower[:-3]}y")
    if lower.endswith(("sses", "shes", "ches", "xes", "zes")) and len(lower) > 4:
        candidates.append(lower[:-2])
    if lower.endswith("ves") and len(lower) > 4:
        candidates.append(f"{lower[:-3]}f")
        candidates.append(f"{lower[:-3]}fe")
    if not lower.endswith(("ss", "us", "is")):
        candidates.append(lower[:-1])

    return list(dict.fromkeys(candidate for candidate in candidates if len(candidate) > 1))


_cached_dictionary: Dict[str, str] | None = None
_cached_reverse_dictionary: Dict[str, str] | None = None
_dictionary_phrase_size_cache: Dict[int, int] = {}


class TranslationResult(TypedDict):
    translation: str
    sourceLanguage: str
    mappedTerms: int
    totalTerms: int
    coverage: float


def get_default_dictionary() -> Dict[str, str]:
    global _cached_dictionary
    if _cached_dictionary is not None:
        return _cached_dictionary
    raw = Path(__file__).resolve().parent.parent.joinpath("vocabulary.json").read_text(encoding="utf-8")
    _cached_dictionary = build_dictionary_from_raw_vocabulary(raw)
    return _cached_dictionary


def get_default_reverse_dictionary() -> Dict[str, str]:
    global _cached_reverse_dictionary
    if _cached_reverse_dictionary is not None:
        return _cached_reverse_dictionary
    raw = Path(__file__).resolve().parent.parent.joinpath("vocabulary.json").read_text(encoding="utf-8")
    _cached_reverse_dictionary = build_reverse_dictionary(get_default_dictionary())
    add_reverse_entries_from_structured_vocabulary(raw, _cached_reverse_dictionary)
    return _cached_reverse_dictionary


def get_max_dictionary_phrase_size(dictionary: Dict[str, str]) -> int:
    cache_key = id(dictionary)
    if cache_key in _dictionary_phrase_size_cache:
        return _dictionary_phrase_size_cache[cache_key]
    max_phrase_size = min(max((len(key.split()) for key in dictionary), default=1), 12)
    _dictionary_phrase_size_cache[cache_key] = max_phrase_size
    return max_phrase_size


def translate_to_ancient_language(
    text: str,
    dictionary: Dict[str, str] | None = None,
    source_language: str = "auto"
) -> TranslationResult:
    dictionary = dictionary or get_default_dictionary()
    input_text = normalize_apostrophes((text or "").strip())
    if not input_text:
        return {"translation": "", "sourceLanguage": "unknown", "mappedTerms": 0, "totalTerms": 0, "coverage": 0}

    forced_italian = source_language.lower() == "italian"
    forced_english = source_language.lower() == "english"
    is_italian_input = forced_italian or (not forced_english and detect_likely_italian(input_text))
    allow_italian_fallback = not forced_english
    normalized_input = input_text if is_italian_input else expand_english_contractions(input_text)
    tokens = tokenize(normalized_input)
    max_phrase_size = get_max_dictionary_phrase_size(dictionary)

    output: List[str] = []
    mapped_terms = 0
    total_terms = 0

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if not is_word(token):
            output.append(token)
            i += 1
            continue

        total_terms += 1
        replaced = False

        for size in range(min(max_phrase_size, len(tokens) - i), 0, -1):
            if i + size > len(tokens):
                continue
            span = tokens[i:i + size]
            if not all(is_word(part) for part in span):
                continue

            source_phrase = " ".join(part.lower() for part in span)
            if is_italian_input:
                translated_phrase = " ".join(ALL_ITALIAN_TO_ENGLISH.get(part.lower(), part.lower()) for part in span)
            else:
                translated_phrase = source_phrase

            ancient = dictionary.get(source_phrase) or dictionary.get(translated_phrase)
            if ancient:
                output.append(ancient)
                mapped_terms += size
                total_terms += size - 1
                i += size
                replaced = True
                break

        if replaced:
            continue

        lower = token.lower()
        italian_as_english = ALL_ITALIAN_TO_ENGLISH.get(lower) if allow_italian_fallback else None
        english_ing_as_base = None
        if not forced_italian:
            english_ing_as_base = next(
                (candidate for candidate in english_ing_candidates(lower) if dictionary.get(candidate)),
                None
            )
        english_plural_as_base = None
        if not forced_italian and not english_ing_as_base:
            english_plural_as_base = next(
                (candidate for candidate in english_plural_candidates(lower) if dictionary.get(candidate)),
                None
            )
        italian_gerund_as_english = None
        if allow_italian_fallback and not italian_as_english:
            for italian_candidate in italian_gerund_candidates(lower):
                english_variant = ALL_ITALIAN_TO_ENGLISH.get(italian_candidate)
                if english_variant:
                    italian_gerund_as_english = english_variant
                    break

        ancient = (
            dictionary.get(lower)
            or (dictionary.get(italian_as_english) if italian_as_english else None)
            or (dictionary.get(english_ing_as_base) if english_ing_as_base else None)
            or (dictionary.get(english_plural_as_base) if english_plural_as_base else None)
            or (dictionary.get(italian_gerund_as_english) if italian_gerund_as_english else None)
        )
        if ancient:
            output.append(ancient)
            mapped_terms += 1
        else:
            output.append(token)
        i += 1

    coverage = 0 if total_terms == 0 else round(mapped_terms / total_terms, 3)
    return {
        "translation": rejoin_tokens(output),
        "sourceLanguage": "italian" if is_italian_input else "english",
        "mappedTerms": mapped_terms,
        "totalTerms": total_terms,
        "coverage": coverage
    }


def build_reverse_dictionary(dictionary: Dict[str, str]) -> Dict[str, str]:
    reverse_dictionary: Dict[str, str] = {}
    for english, ancient in dictionary.items():
        normalized_ancient = normalize_term(ancient)
        if normalized_ancient:
            reverse_dictionary.setdefault(normalized_ancient, english)
            plain_ancient = strip_diacritics(normalized_ancient)
            if plain_ancient != normalized_ancient:
                reverse_dictionary.setdefault(plain_ancient, english)
    return reverse_dictionary


def add_reverse_entry(reverse_dictionary: Dict[str, str], ancient: str, english: str) -> None:
    normalized_ancient = normalize_term(ancient)
    english_variants = split_english_variants(english)
    if not normalized_ancient or not english_variants:
        return
    preferred_english = next((variant for variant in english_variants if not variant.startswith("to ")), english_variants[0])
    reverse_dictionary.setdefault(normalized_ancient, preferred_english)
    plain_ancient = strip_diacritics(normalized_ancient)
    if plain_ancient != normalized_ancient:
        reverse_dictionary.setdefault(plain_ancient, preferred_english)


def add_reverse_entries_from_structured_vocabulary(raw: str, reverse_dictionary: Dict[str, str]) -> None:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return

    def add_nested_forms(value, english: str) -> None:
        if isinstance(value, str):
            add_reverse_entry(reverse_dictionary, value, english)
            return
        if isinstance(value, list):
            for item in value:
                add_nested_forms(item, english)
            return
        if isinstance(value, dict):
            for child in value.values():
                add_nested_forms(child, english)

    def visit(value) -> None:
        if isinstance(value, list):
            for item in value:
                visit(item)
            return

        if not isinstance(value, dict):
            return

        english = value.get("english")
        if isinstance(english, str):
            for key in ANCIENT_VARIANT_KEYS:
                variant = value.get(key)
                if isinstance(variant, str):
                    add_reverse_entry(reverse_dictionary, variant, english)

        translation = value.get("translation")
        if isinstance(translation, str):
            for key in VERB_FORM_KEYS:
                forms = value.get(key)
                if forms is not None:
                    add_nested_forms(forms, translation)

        for child in value.values():
            visit(child)

    visit(parsed)


def lookup_ancient_to_english(source_phrase: str, reverse_dictionary: Dict[str, str]) -> Optional[str]:
    lowered = source_phrase.lower()
    plain = strip_diacritics(lowered)
    return (
        ANCIENT_TO_ENGLISH_ADDITIONS.get(lowered)
        or ANCIENT_TO_ENGLISH_ADDITIONS.get(plain)
        or reverse_dictionary.get(lowered)
        or reverse_dictionary.get(plain)
    )


def translate_from_ancient_language(
    text: str,
    dictionary: Dict[str, str] | None = None,
    reverse_dictionary: Dict[str, str] | None = None
) -> TranslationResult:
    dictionary = dictionary or get_default_dictionary()
    if reverse_dictionary is None:
        reverse_dictionary = get_default_reverse_dictionary() if dictionary is get_default_dictionary() else build_reverse_dictionary(dictionary)
    input_text = normalize_apostrophes((text or "").strip())
    if not input_text:
        return {"translation": "", "sourceLanguage": "unknown", "mappedTerms": 0, "totalTerms": 0, "coverage": 0}

    tokens = tokenize(input_text)
    max_phrase_size = get_max_dictionary_phrase_size(dictionary)
    output: List[str] = []
    mapped_terms = 0
    total_terms = 0

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if not is_word(token):
            output.append(token)
            i += 1
            continue

        total_terms += 1
        replaced = False

        for size in range(min(max_phrase_size, len(tokens) - i), 0, -1):
            if i + size > len(tokens):
                continue
            span = tokens[i:i + size]
            if not all(is_word(part) for part in span):
                continue

            source_phrase = " ".join(part.lower() for part in span)
            english = lookup_ancient_to_english(source_phrase, reverse_dictionary)
            if english:
                output.append(english)
                mapped_terms += size
                total_terms += size - 1
                i += size
                replaced = True
                break

        if replaced:
            continue

        output.append(token)
        i += 1

    coverage = 0 if total_terms == 0 else round(mapped_terms / total_terms, 3)
    return {
        "translation": rejoin_tokens(output),
        "sourceLanguage": "ancient",
        "mappedTerms": mapped_terms,
        "totalTerms": total_terms,
        "coverage": coverage
    }
