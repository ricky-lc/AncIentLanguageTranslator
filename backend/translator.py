import json
import re
from pathlib import Path
from typing import Dict, List, TypedDict

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
IRREGULAR_ITALIAN_GERUNDS = {
    "facendo": "fare",
    "dicendo": "dire",
    "bevendo": "bere",
    "ponendo": "porre",
    "traendo": "trarre"
}


def normalize_apostrophes(text: str) -> str:
    return re.sub(r"[’‘`ʼ]", "'", text)


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
    return [s.strip() for s in re.split(r",|\s+or\s+|\s*/\s*|;", normalized) if s.strip()]


def add_essential_entries(dictionary: Dict[str, str]) -> None:
    for english, ancient in ESSENTIAL_ANCIENT_ADDITIONS.items():
        dictionary.setdefault(english, ancient)


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

    add_essential_entries(dictionary)
    return dictionary


def detect_likely_italian(text: str) -> bool:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žÞþÐð']+", normalize_apostrophes(text.lower()))
    if not words:
        return False
    italian_hits = sum(1 for word in words if word in ITALIAN_TO_ENGLISH)
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
    if len(stem) >= 2 and stem[-1] == stem[-2]:
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
        candidates.extend([f"{root}ere", f"{root}ire", f"{root}are"])
    return list(dict.fromkeys([candidate for candidate in candidates if len(candidate) > 2]))


_cached_dictionary: Dict[str, str] | None = None


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

        for size in range(4, 0, -1):
            if i + size > len(tokens):
                continue
            span = tokens[i:i + size]
            if not all(is_word(part) for part in span):
                continue

            source_phrase = " ".join(part.lower() for part in span)
            if is_italian_input:
                translated_phrase = " ".join(ITALIAN_TO_ENGLISH.get(part.lower(), part.lower()) for part in span)
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
        italian_as_english = ITALIAN_TO_ENGLISH.get(lower) if allow_italian_fallback else None
        english_ing_as_base = next((candidate for candidate in english_ing_candidates(lower) if dictionary.get(candidate)), None)
        italian_gerund_as_english = None
        if allow_italian_fallback and not italian_as_english:
            for italian_candidate in italian_gerund_candidates(lower):
                english_variant = ITALIAN_TO_ENGLISH.get(italian_candidate)
                if english_variant:
                    italian_gerund_as_english = english_variant
                    break

        ancient = (
            dictionary.get(lower)
            or (dictionary.get(italian_as_english) if italian_as_english else None)
            or (dictionary.get(english_ing_as_base) if english_ing_as_base else None)
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
    return reverse_dictionary


def translate_from_ancient_language(
    text: str,
    dictionary: Dict[str, str] | None = None,
    reverse_dictionary: Dict[str, str] | None = None
) -> TranslationResult:
    dictionary = dictionary or get_default_dictionary()
    reverse_dictionary = reverse_dictionary or build_reverse_dictionary(dictionary)
    input_text = normalize_apostrophes((text or "").strip())
    if not input_text:
        return {"translation": "", "sourceLanguage": "unknown", "mappedTerms": 0, "totalTerms": 0, "coverage": 0}

    tokens = tokenize(input_text)
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

        for size in range(4, 0, -1):
            if i + size > len(tokens):
                continue
            span = tokens[i:i + size]
            if not all(is_word(part) for part in span):
                continue

            source_phrase = " ".join(part.lower() for part in span)
            english = reverse_dictionary.get(source_phrase)
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
