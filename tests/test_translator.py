import unittest

from backend.translator import (
    add_reverse_entries_from_structured_vocabulary,
    build_dictionary_from_raw_vocabulary,
    build_reverse_dictionary,
    translate_from_ancient_language,
    translate_to_ancient_language,
)


MOCK_VOCABULARY = """
{
  "entry1": {"english": "fire, flame, blaze", "ancient_language": "brisingr"},
  "entry2": {"english": "water", "ancient_language": "deloi"},
  "entry3": {"english": "thank you", "ancient_language": "thorta"},
  "entry4": {"word": "máttr", "translation": "might, power"},
  "guide": {"example_phrases": ["Atra (let it be)"], "related_words": ["varda (watch over)"]},
  "verbs": {"strong_verbs": [{"infinitive": "glimra", "translation": "to shimmer", "present": {"1st_singular": "glimri"}}, {"infinitive": "waíse", "translation": "to be", "present": {"1st_singular": "eddyr"}}]},
  "entry5": {"english": "book, written scroll", "ancient_language": "bok", "poetic": "bok'ara"},
  "entry6": {"english": "dragon", "ancient_language": "dreki"}
}
"""


class TranslatorTests(unittest.TestCase):
    def test_dictionary_extraction_and_common_word_additions(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        self.assertEqual(dictionary.get("fire"), "brisingr")
        self.assertEqual(dictionary.get("flame"), "brisingr")
        self.assertEqual(dictionary.get("might"), "máttr")
        self.assertEqual(dictionary.get("let it be"), "atra")
        self.assertEqual(dictionary.get("watch over"), "varda")
        self.assertEqual(dictionary.get("shimmer"), "glimra")
        self.assertEqual(dictionary.get("if"), "ef")
        self.assertEqual(dictionary.get("and"), "ok")
        self.assertGreaterEqual(len(dictionary), 220)

    def test_translation_with_common_connectors(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("fire and water", dictionary)
        self.assertEqual(result["translation"], "brisingr ok deloi")
        self.assertEqual(result["sourceLanguage"], "english")

    def test_italian_fallback_translation(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("grazie acqua", dictionary)
        self.assertEqual(result["translation"], "thorta deloi")
        self.assertEqual(result["sourceLanguage"], "italian")

    def test_if_and_isnt_contraction_translation(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("if fire isn't water", dictionary)
        self.assertEqual(result["translation"], "ef brisingr er néiat deloi")

    def test_language_selector_forces_english_or_italian(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        italian_forced = translate_to_ancient_language("grazie acqua", dictionary, source_language="italian")
        english_forced = translate_to_ancient_language("grazie acqua", dictionary, source_language="english")
        self.assertEqual(italian_forced["translation"], "thorta deloi")
        self.assertEqual(english_forced["translation"], "grazie acqua")

    def test_common_words_do_and_make_are_supported(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("do make", dictionary)
        self.assertEqual(result["translation"], "gera gera")

    def test_english_ing_forms_map_to_base_verbs(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("doing making speaking", dictionary)
        self.assertEqual(result["translation"], "gera gera mæla")

    def test_regular_english_plurals_map_to_singular_entries(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("books dragons stars", dictionary)
        self.assertEqual(result["translation"], "bok dreki stjarna")

    def test_italian_gerund_forms_map_to_base_verbs(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_to_ancient_language("facendo parlando", dictionary, source_language="italian")
        self.assertEqual(result["translation"], "gera mæla")

    def test_reverse_translation_from_ancient(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        result = translate_from_ancient_language("ef brisingr er néiat deloi", dictionary)
        self.assertEqual(result["translation"], "if fire is not water")
        self.assertEqual(result["sourceLanguage"], "ancient")

    def test_requested_domain_words_are_translated(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        italian = translate_to_ancient_language("domani matematica test", dictionary, source_language="italian")
        english = translate_to_ancient_language("math test male female", dictionary, source_language="english")
        self.assertEqual(italian["translation"], "á morgin reikningr próf")
        self.assertEqual(english["translation"], "reikningr próf karl kvenna")

    def test_official_phrase_words_translate_from_ancient(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        phrase = "kverst malmr du huildrs edtha, mar frëma né thön eka threyja."
        result = translate_from_ancient_language(phrase, dictionary)
        self.assertEqual(result["translation"], "strength metal you shield maiden and, many fear not those i three.")
        self.assertEqual(result["coverage"], 1.0)

    def test_book_quote_clauses_translate_both_directions(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        english = "May good fortune rule over you, peace live in your heart, and the stars watch over you."
        ancient = "atra esterní ono thelduin, mor'ranr lífa unin hjarta onr, un du evarínya ono varda."
        to_ancient = translate_to_ancient_language(english, dictionary)
        from_ancient = translate_from_ancient_language(ancient, dictionary)
        self.assertEqual(to_ancient["translation"], ancient)
        self.assertEqual(from_ancient["translation"], english.lower())
        self.assertEqual(from_ancient["coverage"], 1.0)

    def test_reverse_dictionary_understands_variant_and_verb_forms(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        reverse_dictionary = build_reverse_dictionary(dictionary)
        add_reverse_entries_from_structured_vocabulary(MOCK_VOCABULARY, reverse_dictionary)
        result = translate_from_ancient_language("bok'ara eddyr glimri", dictionary, reverse_dictionary)
        self.assertEqual(result["translation"], "book be shimmer")
        self.assertEqual(result["coverage"], 1.0)


if __name__ == "__main__":
    unittest.main()
