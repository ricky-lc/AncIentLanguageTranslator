const test = require('node:test');
const assert = require('node:assert/strict');
const { buildDictionaryFromRawVocabulary, translateToAncientLanguage } = require('../src/translator');

const mockVocabulary = `
{
  "entry1": {"english": "fire, flame, blaze", "ancient_language": "brisingr"},
  "entry2": {"english": "water", "ancient_language": "deloi"},
  "entry3": {"english": "thank you", "ancient_language": "thorta"},
  "entry4": {"word": "máttr", "translation": "might, power"}
}
`;

test('buildDictionaryFromRawVocabulary extracts english to ancient pairs', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  assert.equal(dictionary.get('fire'), 'brisingr');
  assert.equal(dictionary.get('flame'), 'brisingr');
  assert.equal(dictionary.get('water'), 'deloi');
  assert.equal(dictionary.get('might'), 'máttr');
});

test('translateToAncientLanguage translates english words', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateToAncientLanguage('fire and water', { dictionary });
  assert.equal(result.translation, 'brisingr ok deloi');
  assert.equal(result.sourceLanguage, 'english');
});

test('translateToAncientLanguage maps Italian words through english fallback', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateToAncientLanguage('grazie acqua', { dictionary });
  assert.equal(result.translation, 'thorta deloi');
  assert.equal(result.sourceLanguage, 'italian');
});

test('translateToAncientLanguage covers missing essentials like if and contractions', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateToAncientLanguage("if fire isn't water", { dictionary });
  assert.equal(result.translation, 'ef brisingr er néiat deloi');
  assert.equal(result.sourceLanguage, 'english');
});
