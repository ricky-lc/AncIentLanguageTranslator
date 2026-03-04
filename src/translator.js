const fs = require('node:fs');
const path = require('node:path');

const ITALIAN_TO_ENGLISH = {
  io: 'i', tu: 'you', lui: 'he', lei: 'she', noi: 'we', voi: 'you all', loro: 'they',
  mi: 'me', me: 'me', ti: 'you', ci: 'us', vi: 'you all',
  mio: 'my', mia: 'my', miei: 'my', mie: 'my', tuo: 'your', tua: 'your', tuoi: 'your', tue: 'your',
  suo: 'his', sua: 'her', suoi: 'their', sue: 'their', nostro: 'our', nostra: 'our',
  il: 'the', lo: 'the', la: 'the', i: 'the', gli: 'the', le: 'the', un: 'a', una: 'a', uno: 'a',
  e: 'and', o: 'or', ma: 'but',
  non: 'not', si: 'yes', no: 'no',
  ciao: 'hello', salve: 'hello', grazie: 'thank you', per: 'for', favore: 'please',
  acqua: 'water', fuoco: 'fire', aria: 'air', terra: 'earth',
  amore: 'love', pace: 'peace', guerra: 'war', luce: 'light', ombra: 'shadow',
  drago: 'dragon', magia: 'magic',
  essere: 'be', sono: 'am', sei: 'are', è: 'is', siamo: 'are', siete: 'are',
  avere: 'have', ho: 'have', hai: 'have', ha: 'has', abbiamo: 'have', hanno: 'have',
  andare: 'go', vado: 'go', vai: 'go', va: 'go',
  vedere: 'see', vedo: 'see', vedi: 'see', vede: 'sees',
  parlare: 'speak', parlo: 'speak', parli: 'speak', parla: 'speaks'
};

const WORD_RE = /[\p{L}\p{M}']+|[^\s\p{L}\p{M}']+/gu;
const DICTIONARY_ENTRY_SPAN_LIMIT = 500;
const ITALIAN_DETECTION_THRESHOLD = 0.2;
const ENGLISH_CONTRACTION_MAP = {
  "isn't": 'is not',
  "aren't": 'are not',
  "wasn't": 'was not',
  "weren't": 'were not',
  "don't": 'do not',
  "doesn't": 'does not',
  "didn't": 'did not',
  "can't": 'cannot',
  "won't": 'will not',
  "i'm": 'i am',
  "you're": 'you are',
  "we're": 'we are',
  "they're": 'they are',
  "it's": 'it is',
  "that's": 'that is',
  "there's": 'there is',
  "i've": 'i have',
  "you've": 'you have',
  "we've": 'we have',
  "they've": 'they have',
  "i'll": 'i will',
  "you'll": 'you will',
  "we'll": 'we will',
  "they'll": 'they will'
};
const ESSENTIAL_ANCIENT_ADDITIONS = {
  and: 'ok',
  or: 'eða',
  but: 'en',
  if: 'ef',
  is: 'er',
  are: 'eru',
  am: 'em',
  was: 'var',
  were: 'váru',
  not: 'néiat',
  yes: 'já',
  no: 'nei',
  to: 'at',
  of: 'af',
  in: 'í',
  on: 'á',
  with: 'með',
  for: 'fyrir',
  from: 'frá',
  have: 'hafa',
  has: 'hefir',
  do: 'gera',
  does: 'gerir',
  can: 'mátt',
  cannot: 'né mátt',
  will: 'mun',
  would: 'myndi',
  should: 'skyldi'
};

function normalizeTerm(text) {
  return text
    .toLowerCase()
    .replace(/\([^)]*\)/g, ' ')
    .replace(/[“”"!?.:]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function splitEnglishVariants(english) {
  const normalized = english
    .toLowerCase()
    .replace(/\([^)]*\)/g, ' ')
    .replace(/[“”"!?.:]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (!normalized) return [];
  return normalized
    .split(/,|\s+or\s+|\s*\/\s*|;/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

function addEssentialEntries(dictionary) {
  for (const [english, ancient] of Object.entries(ESSENTIAL_ANCIENT_ADDITIONS)) {
    if (!dictionary.has(english)) {
      dictionary.set(english, ancient);
    }
  }
}

function normalizeApostrophes(text) {
  return text.replace(/[’‘`]/g, '\'');
}

function buildDictionaryFromRawVocabulary(raw) {
  const dictionary = new Map();
  const pairRegex = new RegExp(
    `"english"\\s*:\\s*"([^"]+)"[\\s\\S]{0,${DICTIONARY_ENTRY_SPAN_LIMIT}}?"ancient_language"\\s*:\\s*"([^"]+)"`,
    'g'
  );
  const reversePairRegex = /"word"\s*:\s*"([^"]+)"\s*,\s*"translation"\s*:\s*"([^"]+)"/g;

  for (const match of raw.matchAll(pairRegex)) {
    const english = match[1];
    const ancient = match[2];
    for (const variant of splitEnglishVariants(english)) {
      if (!dictionary.has(variant)) {
        dictionary.set(variant, ancient);
      }
    }
  }

  for (const match of raw.matchAll(reversePairRegex)) {
    const ancientWord = normalizeTerm(match[1]);
    const english = match[2];
    for (const variant of splitEnglishVariants(english)) {
      if (ancientWord && !dictionary.has(variant)) {
        dictionary.set(variant, ancientWord);
      }
    }
  }

  addEssentialEntries(dictionary);
  return dictionary;
}

let cachedDictionary = null;

function getDefaultDictionary() {
  if (cachedDictionary) return cachedDictionary;
  const vocabularyPath = path.resolve(__dirname, '..', 'vocabulary.json');
  const raw = fs.readFileSync(vocabularyPath, 'utf8');
  cachedDictionary = buildDictionaryFromRawVocabulary(raw);
  return cachedDictionary;
}

function tokenize(text) {
  return text.match(WORD_RE) || [];
}

function expandEnglishContractions(text) {
  return text.replace(/\b[\p{L}\p{M}']+\b/gu, (token) => {
    const lower = token.toLowerCase();
    return ENGLISH_CONTRACTION_MAP[lower] || token;
  });
}

function isWord(token) {
  return /[\p{L}\p{M}']/u.test(token);
}

function detectLikelyItalian(text) {
  const words = (text.toLowerCase().match(/[\p{L}\p{M}']+/gu) || []);
  if (words.length === 0) return false;
  let italianHits = 0;
  for (const word of words) {
    if (ITALIAN_TO_ENGLISH[word]) italianHits += 1;
  }
  return italianHits / words.length >= ITALIAN_DETECTION_THRESHOLD;
}

function rejoinTokens(tokens) {
  let output = '';
  const noLeadingSpace = new Set([',', '.', '!', '?', ';', ':', ')', ']', '}']);
  const noTrailingSpace = new Set(['(', '[', '{']);

  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];
    const prev = tokens[i - 1];
    if (i === 0 || noLeadingSpace.has(token) || noTrailingSpace.has(prev)) {
      output += token;
    } else {
      output += ` ${token}`;
    }
  }

  return output;
}

function translateToAncientLanguage(text, options = {}) {
  const dictionary = options.dictionary || getDefaultDictionary();
  const input = normalizeApostrophes(`${text || ''}`.trim());
  if (!input) {
    return { translation: '', sourceLanguage: 'unknown', mappedTerms: 0, totalTerms: 0 };
  }

  const isItalianInput = detectLikelyItalian(input);
  const normalizedInput = isItalianInput ? input : expandEnglishContractions(input);
  const tokens = tokenize(normalizedInput);
  const output = [];
  let mappedTerms = 0;
  let totalTerms = 0;

  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];

    if (!isWord(token)) {
      output.push(token);
      continue;
    }

    totalTerms += 1;

    let replaced = false;
    for (let size = 4; size >= 1; size -= 1) {
      if (i + size > tokens.length) continue;
      const span = tokens.slice(i, i + size);
      if (!span.every(isWord)) continue;

      const sourcePhrase = span.map((s) => s.toLowerCase()).join(' ');
      const translatedPhrase = isItalianInput
        ? span.map((s) => ITALIAN_TO_ENGLISH[s.toLowerCase()] || s.toLowerCase()).join(' ')
        : sourcePhrase;

      const ancient = dictionary.get(sourcePhrase) || dictionary.get(translatedPhrase);
      if (ancient) {
        output.push(ancient);
        mappedTerms += size;
        totalTerms += (size - 1);
        i += (size - 1);
        replaced = true;
        break;
      }
    }

    if (!replaced) {
      const lower = token.toLowerCase();
      const italianAsEnglish = ITALIAN_TO_ENGLISH[lower];
      const ancient = dictionary.get(lower) || (italianAsEnglish ? dictionary.get(italianAsEnglish) : null);
      if (ancient) {
        output.push(ancient);
        mappedTerms += 1;
      } else {
        output.push(token);
      }
    }
  }

  return {
    translation: rejoinTokens(output),
    sourceLanguage: isItalianInput ? 'italian' : 'english',
    mappedTerms,
    totalTerms,
    coverage: totalTerms === 0 ? 0 : Number((mappedTerms / totalTerms).toFixed(3))
  };
}

module.exports = {
  addEssentialEntries,
  buildDictionaryFromRawVocabulary,
  detectLikelyItalian,
  translateToAncientLanguage
};
