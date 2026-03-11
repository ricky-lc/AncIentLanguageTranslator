const fs = require('node:fs');
const path = require('node:path');

const ITALIAN_TO_ENGLISH = {
  io: 'i', tu: 'you', lui: 'he', lei: 'she', noi: 'we', voi: 'you all', loro: 'they',
  mi: 'me', me: 'me', ti: 'you', ci: 'us', vi: 'you all',
  mio: 'my', mia: 'my', miei: 'my', mie: 'my', tuo: 'your', tua: 'your', tuoi: 'your', tue: 'your',
  suo: 'his', sua: 'her', suoi: 'their', sue: 'their', nostro: 'our', nostra: 'our',
  il: 'the', lo: 'the', la: 'the', i: 'the', gli: 'the', le: 'the', un: 'a', una: 'a', uno: 'a',
  e: 'and', o: 'or', ma: 'but', se: 'if', non: 'not', si: 'yes', no: 'no',
  ciao: 'hello', salve: 'hello', grazie: 'thank you', per: 'for', favore: 'please',
  acqua: 'water', fuoco: 'fire', aria: 'air', terra: 'earth',
  amore: 'love', pace: 'peace', guerra: 'war', luce: 'light', ombra: 'shadow',
  drago: 'dragon', magia: 'magic',
  essere: 'be', sono: 'am', sei: 'are', è: 'is', siamo: 'are', siete: 'are',
  avere: 'have', ho: 'have', hai: 'have', ha: 'has', abbiamo: 'have', hanno: 'have',
  andare: 'go', vado: 'go', vai: 'go', va: 'go', venire: 'come', vengo: 'come',
  fare: 'do', faccio: 'do', fa: 'does', dire: 'say', dico: 'say',
  parlare: 'speak', parlo: 'speak', parli: 'speak', parla: 'speaks',
  vedere: 'see', vedo: 'see', vedi: 'see', vede: 'sees',
  chi: 'who', cosa: 'what', dove: 'where', quando: 'when', come: 'how', perché: 'why'
};

const EXTENDED_ITALIAN_TO_ENGLISH = {
  domani: 'tomorrow', oggi: 'today', ieri: 'yesterday', adesso: 'now',
  matematica: 'math', test: 'test', esame: 'exam', scuola: 'school', classe: 'class',
  insegnante: 'teacher', studente: 'student', studio: 'study', imparo: 'learn',
  libro: 'book', penna: 'pen', carta: 'paper', computer: 'computer', telefono: 'phone',
  internet: 'internet', programma: 'program', progetto: 'project', codice: 'code',
  errore: 'error', soluzione: 'solution', sistema: 'system', dati: 'data',
  numero: 'number', tempo: 'time', giorno: 'day', notte: 'night',
  casa: 'house', città: 'city', strada: 'road', mondo: 'world',
  uomo: 'man', donna: 'woman', maschio: 'male', femmina: 'female',
  ragazzo: 'boy', ragazza: 'girl', bambino: 'child', famiglia: 'family',
  padre: 'father', madre: 'mother', fratello: 'brother', sorella: 'sister',
  amico: 'friend', nemico: 'enemy', re: 'king', regina: 'queen',
  forza: 'strength', potere: 'power', sapere: 'knowledge', verità: 'truth',
  ordine: 'order', caos: 'chaos', vita: 'life', morte: 'death',
  felice: 'happy', triste: 'sad', forte: 'strong', debole: 'weak',
  grande: 'big', piccolo: 'small', veloce: 'fast', lento: 'slow',
  caldo: 'hot', freddo: 'cold', alto: 'high', basso: 'low',
  vicino: 'near', lontano: 'far', destra: 'right', sinistra: 'left',
  aprire: 'open', apro: 'open', chiudere: 'close', chiudo: 'close',
  iniziare: 'start', inizio: 'start', finire: 'finish', finisco: 'finish',
  correre: 'run', corro: 'run', camminare: 'walk', cammino: 'walk',
  leggere: 'read', leggo: 'read', scrivere: 'write', scrivo: 'write',
  pensare: 'think', penso: 'think', creare: 'create', creo: 'create',
  costruire: 'build', costruisco: 'build', usare: 'use', uso: 'use',
  provare: 'test', provo: 'test', controllare: 'check', controllo: 'check'
};

const ALL_ITALIAN_TO_ENGLISH = { ...ITALIAN_TO_ENGLISH, ...EXTENDED_ITALIAN_TO_ENGLISH };

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
  and: 'ok', or: 'eða', but: 'en', if: 'ef', then: 'þá', because: 'því',
  the: 'sá', is: 'er', are: 'eru', am: 'em', was: 'var', were: 'váru',
  be: 'vera', being: 'verandi', been: 'verit', not: 'néiat', yes: 'já', no: 'nei',
  to: 'at', of: 'af', in: 'í', on: 'á', with: 'með', for: 'fyrir', from: 'frá',
  into: 'inn í', out: 'út', under: 'undir', over: 'yfir', before: 'fyrir', after: 'eptir',
  have: 'hafa', has: 'hefir', had: 'hafði', do: 'gera', does: 'gerir', did: 'gerði',
  can: 'mátt', cannot: 'né mátt', could: 'mátti', will: 'mun', would: 'myndi', should: 'skyldi',
  must: 'skal', may: 'megi', make: 'gera', go: 'ganga', come: 'koma', see: 'sjá',
  know: 'kenna', say: 'segja', speak: 'mæla', think: 'hugsa', want: 'vilja', need: 'þurfa',
  give: 'gefa', take: 'taka', find: 'finna', tell: 'segja', ask: 'spyrja',
  who: 'hver', what: 'hvat', where: 'hvar', when: 'hvenær', why: 'hví', how: 'hvernig',
  all: 'allr', any: 'einhverr', each: 'hverr', every: 'hverr', both: 'báðir', either: 'annarr hvárr',
  neither: 'engi', some: 'sumr', many: 'margir', more: 'meira', most: 'mest', few: 'fáir',
  very: 'mjök', much: 'mikit', little: 'lítit', good: 'góðr', bad: 'illr',
  true: 'sannr', new: 'nýr', old: 'forn', first: 'fyrstr', last: 'síðastr',
  today: 'í dag', tomorrow: 'á morgin', yesterday: 'í gær', now: 'nú', always: 'æ', never: 'aldri',
  while: 'meðan', unless: 'nema', than: 'en', as: 'sem',
  please: 'blítt', hello: 'heill', thanks: 'þakkir', thank: 'þakka'
};

const EXTENDED_ESSENTIAL_ANCIENT_ADDITIONS = {
  a: 'einn', an: 'einn', this: 'þessi', that: 'sá', these: 'þessir', those: 'þeir',
  i: 'ek', you: 'þú', he: 'hann', she: 'hún', it: 'þat', we: 'vér', they: 'þeir',
  my: 'mín', your: 'þín', our: 'vár', their: 'þeirra', his: 'hans', her: 'hennar',
  me: 'mik', him: 'hann', us: 'oss', them: 'þá',
  at: 'at', by: 'við', about: 'um', through: 'gegnum', between: 'milli', against: 'gegn',
  during: 'um', without: 'án', within: 'innan', around: 'kring', above: 'yfir', below: 'undir',
  up: 'upp', down: 'niðr', left: 'vinstri', right: 'hægri', near: 'nær', far: 'fjarri',
  again: 'aptr', soon: 'brátt', late: 'seint', early: 'árla', already: 'þegar', still: 'enn',
  tonight: 'í nótt', morning: 'morginn', evening: 'kveld', day: 'dagr', night: 'nótt',
  time: 'tími', year: 'ár', month: 'mánuðr', week: 'vika', hour: 'stund', minute: 'mínúta',
  man: 'maðr', woman: 'kona', male: 'karl', female: 'kvenna',
  boy: 'drengr', girl: 'mær', child: 'barn', children: 'börn',
  person: 'maðr', people: 'fólk', friend: 'vinr', enemy: 'óvinr',
  family: 'ætt', father: 'faðir', mother: 'móðir', brother: 'bróðir', sister: 'systir',
  king: 'konungr', queen: 'drottning', warrior: 'drengr', mage: 'galdramaðr',
  house: 'hús', home: 'heimr', city: 'borg', village: 'þorp', road: 'vegr', world: 'heimr',
  land: 'land', sea: 'sær', sky: 'himinn', sun: 'sól', moon: 'máni', star: 'stjarna',
  stone: 'steinn', metal: 'járn', wood: 'viðr', blood: 'blóð', heart: 'hjarta', mind: 'hugr',
  truth: 'sannleikr', lie: 'lygi', law: 'lög', order: 'skipan', chaos: 'óskipan',
  life: 'líf', death: 'dauði', strength: 'afl', power: 'máttr', magic: 'galdr', knowledge: 'vísdómr',
  work: 'verk', job: 'starf', task: 'verk', problem: 'vandi', solution: 'lausn',
  question: 'spurning', answer: 'svar', idea: 'hugmynd', story: 'saga', name: 'nafn',
  language: 'tunga', word: 'orð', sentence: 'setning', book: 'bók', letter: 'stafr',
  number: 'tala', math: 'reikningr', mathematics: 'reikningr', science: 'vísindi',
  school: 'skóli', class: 'bekkr', teacher: 'kennari', student: 'nemi',
  study: 'nema', learn: 'nema', teach: 'kenna', read: 'lesa', write: 'rita',
  code: 'kóði', program: 'forrit', project: 'verk', system: 'kerfi', data: 'gögn',
  network: 'net', computer: 'tölva', phone: 'sími', internet: 'net', message: 'boð',
  open: 'opna', close: 'lúka', start: 'hefja', finish: 'ljúka', begin: 'hefja', end: 'endi',
  build: 'smíða', create: 'skapa', use: 'nota', check: 'kanna', test: 'próf', exam: 'próf',
  run: 'renna', walk: 'ganga', stop: 'stöðva', turn: 'snúa', move: 'hreyfa',
  bring: 'færa', send: 'senda', receive: 'taka', help: 'hjálpa', protect: 'verja',
  attack: 'ráðast', win: 'sigra', lose: 'tapa', save: 'bjarga',
  hot: 'heitr', cold: 'kaldr', big: 'stórr', small: 'lítill', long: 'langr', short: 'stuttr',
  young: 'ungr', happy: 'glaðr', sad: 'sorgmæddr', strong: 'sterkr', weak: 'veikr',
  easy: 'auðveldr', hard: 'erfiðr', important: 'mikilvægr', different: 'ólíkr',
  same: 'sami', free: 'frjáls', safe: 'öruggr', ready: 'búinn',
  one: 'einn', two: 'tveir', three: 'þrír', four: 'fjórir', five: 'fimm',
  six: 'sex', seven: 'sjau', eight: 'átta', nine: 'níu', ten: 'tíu'
};

const CANONICAL_BOOK_PHRASES = {
  'let it be': 'atra',
  'may good fortune rule over you': 'atra esterní ono thelduin',
  'peace live in your heart': "mor'ranr lífa unin hjarta onr",
  'the stars watch over you': 'du evarínya ono varda',
  'and the stars watch over you': 'un du evarínya ono varda'
};

const ALL_ESSENTIAL_ANCIENT_ADDITIONS = {
  ...ESSENTIAL_ANCIENT_ADDITIONS,
  ...EXTENDED_ESSENTIAL_ANCIENT_ADDITIONS,
  ...CANONICAL_BOOK_PHRASES
};

const ANCIENT_TO_ENGLISH_ADDITIONS = {
  kverst: 'strength',
  malmr: 'metal',
  du: 'you',
  huildrs: 'shield maiden',
  edtha: 'and',
  mar: 'many',
  'frëma': 'fear',
  'né': 'not',
  'thön': 'those',
  eka: 'i',
  threyja: 'three',
  'kverst malmr du huildrs edtha mar frëma né thön eka threyja': 'strength and steel, shield-maiden; many fear those three, but i do not'
};

const IRREGULAR_ITALIAN_GERUNDS = {
  facendo: 'fare',
  dicendo: 'dire',
  bevendo: 'bere',
  ponendo: 'porre',
  traendo: 'trarre'
};
const GLOSS_STRING_KEYS = new Set(['related_words', 'components', 'example_phrases', 'example', 'base_example', 'compounds']);
const ANCIENT_VARIANT_KEYS = ['ancient_language', 'formal', 'informal', 'poetic', 'archaic'];
const VERB_FORM_KEYS = ['present', 'past', 'future', 'subjunctive', 'imperative', 'participles'];
const DICTIONARY_PHRASE_SIZE_CACHE = new WeakMap();

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
  const variants = normalized
    .split(/,|\s+or\s+|\s*\/\s*|;/g)
    .map((s) => s.trim())
    .filter(Boolean);
  const expanded = [];
  for (const variant of variants) {
    expanded.push(variant);
    if (variant.startsWith('to ') && variant.length > 3) {
      expanded.push(variant.slice(3).trim());
    }
  }
  return [...new Set(expanded.filter(Boolean))];
}

function addEssentialEntries(dictionary) {
  for (const [english, ancient] of Object.entries(ALL_ESSENTIAL_ANCIENT_ADDITIONS)) {
    if (!dictionary.has(english)) {
      dictionary.set(english, ancient);
    }
  }
}

function addNormalizedEntry(dictionary, english, ancient) {
  const normalizedAncient = normalizeTerm(ancient);
  if (!normalizedAncient) return;
  for (const variant of splitEnglishVariants(english)) {
    if (!dictionary.has(variant)) {
      dictionary.set(variant, normalizedAncient);
    }
  }
}

const IRREGULAR_ENGLISH_DEGREES = {
  good: ['better', 'best'],
  well: ['better', 'best'],
  bad: ['worse', 'worst'],
  ill: ['worse', 'worst'],
  little: ['less', 'least'],
  many: ['more', 'most'],
  much: ['more', 'most'],
  far: ['farther', 'farthest'],
  great: ['greater', 'greatest']
};

function buildEnglishDegreeForms(english) {
  const comparatives = [];
  const superlatives = [];
  for (const variant of splitEnglishVariants(english)) {
    if (!/^[a-z]+$/.test(variant)) continue;
    if (IRREGULAR_ENGLISH_DEGREES[variant]) {
      const [comparative, superlative] = IRREGULAR_ENGLISH_DEGREES[variant];
      comparatives.push(comparative);
      superlatives.push(superlative);
      continue;
    }
    if (variant.length <= 2) continue;
    if (variant.endsWith('y') && variant.length > 2 && !'aeiou'.includes(variant[variant.length - 2])) {
      const stem = variant.slice(0, -1);
      comparatives.push(`${stem}ier`);
      superlatives.push(`${stem}iest`);
      continue;
    }
    if (variant.endsWith('e')) {
      comparatives.push(`${variant}r`);
      superlatives.push(`${variant}st`);
      continue;
    }
    if (
      variant.length >= 3
      && !'aeiouwxy'.includes(variant[variant.length - 1])
      && 'aeiou'.includes(variant[variant.length - 2])
      && !'aeiou'.includes(variant[variant.length - 3])
    ) {
      comparatives.push(`${variant}${variant[variant.length - 1]}er`);
      superlatives.push(`${variant}${variant[variant.length - 1]}est`);
      continue;
    }
    comparatives.push(`${variant}er`);
    superlatives.push(`${variant}est`);
  }
  return [new Set(comparatives), new Set(superlatives)];
}

function addGlossEntriesFromStructuredVocabulary(raw, dictionary) {
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return;
  }

  const visit = (value, parentKey = '') => {
    if (Array.isArray(value)) {
      for (const item of value) visit(item, parentKey);
      return;
    }

    if (value && typeof value === 'object') {
      if (typeof value.infinitive === 'string' && typeof value.translation === 'string') {
        addNormalizedEntry(dictionary, value.translation, value.infinitive);
      }
      if (typeof value.base === 'string' && typeof value.translation === 'string') {
        addNormalizedEntry(dictionary, value.translation, value.base);
        const [comparatives, superlatives] = buildEnglishDegreeForms(value.translation);
        if (typeof value.comparative === 'string') {
          for (const englishComparative of comparatives) {
            addNormalizedEntry(dictionary, englishComparative, value.comparative);
          }
        }
        if (typeof value.superlative === 'string') {
          for (const englishSuperlative of superlatives) {
            addNormalizedEntry(dictionary, englishSuperlative, value.superlative);
          }
        }
      }
      for (const [key, child] of Object.entries(value)) {
        visit(child, key);
      }
      return;
    }

    if (typeof value === 'string' && GLOSS_STRING_KEYS.has(parentKey)) {
      const match = value.match(/^\s*([^()]+?)\s*\(([^()]+)\)\s*$/u);
      if (match) {
        addNormalizedEntry(dictionary, match[2], match[1]);
      }
    }
  };

  visit(parsed);
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

  addGlossEntriesFromStructuredVocabulary(raw, dictionary);
  addEssentialEntries(dictionary);
  return dictionary;
}

let cachedDictionary = null;
let cachedReverseDictionary = null;

function getDefaultDictionary() {
  if (cachedDictionary) return cachedDictionary;
  const vocabularyPath = path.resolve(__dirname, '..', 'vocabulary.json');
  const raw = fs.readFileSync(vocabularyPath, 'utf8');
  cachedDictionary = buildDictionaryFromRawVocabulary(raw);
  return cachedDictionary;
}

function getDefaultReverseDictionary() {
  if (cachedReverseDictionary) return cachedReverseDictionary;
  const vocabularyPath = path.resolve(__dirname, '..', 'vocabulary.json');
  const raw = fs.readFileSync(vocabularyPath, 'utf8');
  cachedReverseDictionary = buildReverseDictionary(getDefaultDictionary());
  addReverseEntriesFromStructuredVocabulary(raw, cachedReverseDictionary);
  return cachedReverseDictionary;
}

function tokenize(text) {
  return text.match(WORD_RE) || [];
}

function getMaxDictionaryPhraseSize(dictionary) {
  if (DICTIONARY_PHRASE_SIZE_CACHE.has(dictionary)) {
    return DICTIONARY_PHRASE_SIZE_CACHE.get(dictionary);
  }
  let maxPhraseSize = 1;
  for (const key of dictionary.keys()) {
    const size = key.split(/\s+/).filter(Boolean).length;
    if (size > maxPhraseSize) maxPhraseSize = size;
  }
  maxPhraseSize = Math.min(maxPhraseSize, 12);
  DICTIONARY_PHRASE_SIZE_CACHE.set(dictionary, maxPhraseSize);
  return maxPhraseSize;
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
    if (ALL_ITALIAN_TO_ENGLISH[word]) italianHits += 1;
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

function englishIngCandidates(word) {
  const lower = word.toLowerCase();
  if (!lower.endsWith('ing') || lower.length <= 4) return [];
  const stem = lower.slice(0, -3);
  const candidates = [stem];
  if (stem.length >= 2 && stem[stem.length - 1] === stem[stem.length - 2] && !'aeiou'.includes(stem[stem.length - 1])) {
    candidates.push(stem.slice(0, -1));
  }
  if (stem && !'aeiou'.includes(stem[stem.length - 1])) {
    candidates.push(`${stem}e`);
  }
  return [...new Map(candidates.filter(Boolean).map((c) => [c, c])).keys()];
}

function italianGerundCandidates(word) {
  const lower = word.toLowerCase();
  if (lower.length <= 5) return [];
  if (IRREGULAR_ITALIAN_GERUNDS[lower]) return [IRREGULAR_ITALIAN_GERUNDS[lower]];
  const candidates = [];
  if (lower.endsWith('ando')) {
    const root = lower.slice(0, -4);
    candidates.push(`${root}are`, `${root}ere`, `${root}ire`);
  }
  if (lower.endsWith('endo')) {
    const root = lower.slice(0, -4);
    candidates.push(`${root}are`, `${root}ere`, `${root}ire`);
  }
  return [...new Map(candidates.filter((c) => c.length > 2).map((c) => [c, c])).keys()];
}

function englishPluralCandidates(word) {
  const lower = word.toLowerCase();
  if (lower.length <= 3 || !lower.endsWith('s')) return [];
  const candidates = [];
  if (lower.endsWith('ies') && lower.length > 4) {
    candidates.push(`${lower.slice(0, -3)}y`);
  }
  if (/(sses|shes|ches|xes|zes)$/.test(lower) && lower.length > 4) {
    candidates.push(lower.slice(0, -2));
  }
  if (lower.endsWith('ves') && lower.length > 4) {
    candidates.push(`${lower.slice(0, -3)}f`, `${lower.slice(0, -3)}fe`);
  }
  if (!/(ss|us|is)$/.test(lower)) {
    candidates.push(lower.slice(0, -1));
  }
  return [...new Set(candidates.filter((candidate) => candidate.length > 1))];
}

function translateToAncientLanguage(text, options = {}) {
  const dictionary = options.dictionary || getDefaultDictionary();
  const sourceLanguage = (options.sourceLanguage || 'auto').toLowerCase();
  const input = normalizeApostrophes(`${text || ''}`.trim());
  if (!input) {
    return { translation: '', sourceLanguage: 'unknown', mappedTerms: 0, totalTerms: 0, coverage: 0 };
  }

  const forcedItalian = sourceLanguage === 'italian';
  const forcedEnglish = sourceLanguage === 'english';
  const isItalianInput = forcedItalian || (!forcedEnglish && detectLikelyItalian(input));
  const allowItalianFallback = !forcedEnglish;
  const normalizedInput = isItalianInput ? input : expandEnglishContractions(input);
  const tokens = tokenize(normalizedInput);
  const maxPhraseSize = getMaxDictionaryPhraseSize(dictionary);
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
    for (let size = Math.min(maxPhraseSize, tokens.length - i); size >= 1; size -= 1) {
      if (i + size > tokens.length) continue;
      const span = tokens.slice(i, i + size);
      if (!span.every(isWord)) continue;

      const sourcePhrase = span.map((s) => s.toLowerCase()).join(' ');
      const translatedPhrase = isItalianInput
        ? span.map((s) => ALL_ITALIAN_TO_ENGLISH[s.toLowerCase()] || s.toLowerCase()).join(' ')
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
      const italianAsEnglish = allowItalianFallback ? ALL_ITALIAN_TO_ENGLISH[lower] : null;
      let engIngBase = null;
      if (!forcedItalian) {
        engIngBase = englishIngCandidates(lower).find((c) => dictionary.has(c)) || null;
      }
      let englishPluralBase = null;
      if (!forcedItalian && !engIngBase) {
        englishPluralBase = englishPluralCandidates(lower).find((c) => dictionary.has(c)) || null;
      }
      let italianGerundAsEnglish = null;
      if (allowItalianFallback && !italianAsEnglish) {
        for (const candidate of italianGerundCandidates(lower)) {
          const eng = ALL_ITALIAN_TO_ENGLISH[candidate];
          if (eng) { italianGerundAsEnglish = eng; break; }
        }
      }
      const ancient = dictionary.get(lower)
        || (italianAsEnglish ? dictionary.get(italianAsEnglish) : null)
        || (engIngBase ? dictionary.get(engIngBase) : null)
        || (englishPluralBase ? dictionary.get(englishPluralBase) : null)
        || (italianGerundAsEnglish ? dictionary.get(italianGerundAsEnglish) : null);
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

function stripDiacritics(text) {
  return text.normalize('NFD').replace(/\p{Mn}/gu, '');
}

function buildReverseDictionary(dictionary) {
  const reverse = new Map();
  for (const [english, ancient] of dictionary) {
    const normalized = normalizeTerm(ancient);
    if (normalized && !reverse.has(normalized)) reverse.set(normalized, english);
    const plain = stripDiacritics(normalized);
    if (plain !== normalized && !reverse.has(plain)) reverse.set(plain, english);
  }
  return reverse;
}

function addReverseEntry(reverseDictionary, ancient, english) {
  const normalizedAncient = normalizeTerm(ancient);
  const englishVariants = splitEnglishVariants(english);
  if (!normalizedAncient || englishVariants.length === 0) return;
  const preferredEnglish = englishVariants.find((variant) => !variant.startsWith('to ')) || englishVariants[0];
  if (!reverseDictionary.has(normalizedAncient)) reverseDictionary.set(normalizedAncient, preferredEnglish);
  const plainAncient = stripDiacritics(normalizedAncient);
  if (plainAncient !== normalizedAncient && !reverseDictionary.has(plainAncient)) {
    reverseDictionary.set(plainAncient, preferredEnglish);
  }
}

function addReverseEntriesFromStructuredVocabulary(raw, reverseDictionary) {
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return;
  }

  const addNestedForms = (value, english) => {
    if (typeof value === 'string') {
      addReverseEntry(reverseDictionary, value, english);
      return;
    }
    if (Array.isArray(value)) {
      for (const item of value) addNestedForms(item, english);
      return;
    }
    if (value && typeof value === 'object') {
      for (const child of Object.values(value)) addNestedForms(child, english);
    }
  };

  const visit = (value) => {
    if (Array.isArray(value)) {
      for (const item of value) visit(item);
      return;
    }
    if (!value || typeof value !== 'object') return;

    if (typeof value.english === 'string') {
      for (const key of ANCIENT_VARIANT_KEYS) {
        if (typeof value[key] === 'string') {
          addReverseEntry(reverseDictionary, value[key], value.english);
        }
      }
    }

    if (typeof value.translation === 'string') {
      for (const key of VERB_FORM_KEYS) {
        if (value[key] !== undefined) {
          addNestedForms(value[key], value.translation);
        }
      }
    }

    for (const child of Object.values(value)) {
      visit(child);
    }
  };

  visit(parsed);
}

function lookupAncientToEnglish(sourcePhrase, reverseDictionary) {
  const lowered = sourcePhrase.toLowerCase();
  const plain = stripDiacritics(lowered);
  return ANCIENT_TO_ENGLISH_ADDITIONS[lowered]
    || ANCIENT_TO_ENGLISH_ADDITIONS[plain]
    || reverseDictionary.get(lowered)
    || reverseDictionary.get(plain)
    || null;
}

function translateFromAncientLanguage(text, options = {}) {
  const dictionary = options.dictionary || getDefaultDictionary();
  const reverseDictionary = options.reverseDictionary
    || (dictionary === getDefaultDictionary() ? getDefaultReverseDictionary() : buildReverseDictionary(dictionary));
  const input = normalizeApostrophes(`${text || ''}`.trim());
  if (!input) {
    return { translation: '', sourceLanguage: 'unknown', mappedTerms: 0, totalTerms: 0, coverage: 0 };
  }

  const tokens = tokenize(input);
  const maxPhraseSize = getMaxDictionaryPhraseSize(dictionary);
  const normalizedInputPhrase = tokens.filter(isWord).map((token) => token.toLowerCase()).join(' ');
  const exactPhraseTranslation = normalizedInputPhrase ? lookupAncientToEnglish(normalizedInputPhrase, reverseDictionary) : null;
  if (exactPhraseTranslation) {
    const wordCount = normalizedInputPhrase.split(/\s+/).filter(Boolean).length;
    const trailingPunctuation = input.match(/([,.;:!?]+)\s*$/u)?.[1] || '';
    return {
      translation: `${exactPhraseTranslation}${trailingPunctuation}`,
      sourceLanguage: 'ancient',
      mappedTerms: wordCount,
      totalTerms: wordCount,
      coverage: 1
    };
  }

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

    for (let size = Math.min(maxPhraseSize, tokens.length - i); size >= 1; size -= 1) {
      if (i + size > tokens.length) continue;
      const span = tokens.slice(i, i + size);
      if (!span.every(isWord)) continue;

      const sourcePhrase = span.map((s) => s.toLowerCase()).join(' ');
      const english = lookupAncientToEnglish(sourcePhrase, reverseDictionary);
      if (english) {
        output.push(english);
        mappedTerms += size;
        totalTerms += (size - 1);
        i += (size - 1);
        replaced = true;
        break;
      }
    }

    if (!replaced) {
      output.push(token);
    }
  }

  const coverage = totalTerms === 0 ? 0 : Number((mappedTerms / totalTerms).toFixed(3));
  return {
    translation: rejoinTokens(output),
    sourceLanguage: 'ancient',
    mappedTerms,
    totalTerms,
    coverage
  };
}

module.exports = {
  addEssentialEntries,
  addReverseEntriesFromStructuredVocabulary,
  buildDictionaryFromRawVocabulary,
  buildReverseDictionary,
  detectLikelyItalian,
  getDefaultReverseDictionary,
  translateToAncientLanguage,
  translateFromAncientLanguage
};
