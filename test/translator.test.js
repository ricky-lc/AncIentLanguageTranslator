const test = require('node:test');
const assert = require('node:assert/strict');
const { buildDictionaryFromRawVocabulary, buildReverseDictionary, translateToAncientLanguage, translateFromAncientLanguage } = require('../src/translator');

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

test('buildDictionaryFromRawVocabulary includes essential common word additions', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  assert.equal(dictionary.get('if'), 'ef');
  assert.equal(dictionary.get('and'), 'ok');
  assert.ok(dictionary.size >= 220);
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

test('translateToAncientLanguage language selector forces english or italian', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const italianForced = translateToAncientLanguage('grazie acqua', { dictionary, sourceLanguage: 'italian' });
  const englishForced = translateToAncientLanguage('grazie acqua', { dictionary, sourceLanguage: 'english' });
  assert.equal(italianForced.translation, 'thorta deloi');
  assert.equal(englishForced.translation, 'grazie acqua');
});

test('translateToAncientLanguage do and make are both supported', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateToAncientLanguage('do make', { dictionary });
  assert.equal(result.translation, 'gera gera');
});

test('translateToAncientLanguage english -ing forms map to base verbs', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateToAncientLanguage('doing making speaking', { dictionary });
  assert.equal(result.translation, 'gera gera mæla');
});

test('translateToAncientLanguage italian gerund forms map to base verbs', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateToAncientLanguage('facendo parlando', { dictionary, sourceLanguage: 'italian' });
  assert.equal(result.translation, 'gera mæla');
});

test('translateToAncientLanguage requested domain words are translated', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const italian = translateToAncientLanguage('domani matematica test', { dictionary, sourceLanguage: 'italian' });
  const english = translateToAncientLanguage('math test male female', { dictionary, sourceLanguage: 'english' });
  assert.equal(italian.translation, 'á morgin reikningr próf');
  assert.equal(english.translation, 'reikningr próf karl kvenna');
});

test('translateFromAncientLanguage reverses ancient to english', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const result = translateFromAncientLanguage('ef brisingr er néiat deloi', { dictionary });
  assert.equal(result.translation, 'if fire is not water');
  assert.equal(result.sourceLanguage, 'ancient');
});

test('translateFromAncientLanguage handles the official phrase', () => {
  const dictionary = buildDictionaryFromRawVocabulary(mockVocabulary);
  const phrase = 'kverst malmr du huildrs edtha, mar frëma né thön eka threyja.';
  const result = translateFromAncientLanguage(phrase, { dictionary });
  assert.equal(result.translation, 'strength metal you shield maiden and, many fear not those i three.');
  assert.equal(result.coverage, 1);
});
