import unittest

from backend.translator import build_dictionary_from_raw_vocabulary, translate_to_ancient_language


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


if __name__ == "__main__":
    unittest.main()
