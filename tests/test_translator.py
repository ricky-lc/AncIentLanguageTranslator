import unittest

from backend.translator import (
    build_dictionary_from_raw_vocabulary,
    translate_from_ancient_language,
    translate_to_ancient_language,
)


MOCK_VOCABULARY = """
{
  "entry1": {"english": "fire, flame, blaze", "ancient_language": "brisingr"},
  "entry2": {"english": "water", "ancient_language": "deloi"},
  "entry3": {"english": "thank you", "ancient_language": "thorta"},
  "entry4": {"word": "máttr", "translation": "might, power"}
}
"""


class TranslatorTests(unittest.TestCase):
    def test_dictionary_extraction_and_common_word_additions(self):
        dictionary = build_dictionary_from_raw_vocabulary(MOCK_VOCABULARY)
        self.assertEqual(dictionary.get("fire"), "brisingr")
        self.assertEqual(dictionary.get("flame"), "brisingr")
        self.assertEqual(dictionary.get("might"), "máttr")
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


if __name__ == "__main__":
    unittest.main()
