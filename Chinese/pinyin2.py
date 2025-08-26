# Libraries
import hanlp
from pypinyin import pinyin, Style
import sys
from googletrans import Translator

# Models
tokenizer = hanlp.load('CTB9_TOK_ELECTRA_BASE')
pos_tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)
translator = Translator()

# Dictionary for POS tags
pos_dict = {
    'NN': 'common noun',
    'NR': 'proper noun',
    'NT': 'temporal noun',
    'LC': 'localizer',
    'PN': 'pronoun',
    'DT': 'determiner',
    'CD': 'cardinal number',
    'OD': 'ordinal number',
    'M': 'measure word',
    'VA': 'verb',
    'VC': 'verb',
    'VE': 'verb',
    'VV': 'verb',
    'AD': 'adverb',
    'P': 'preposition',
    'CS': 'subordinating conjunction',
    'CC': 'conjunction',
    'DEC': 'particle',
    'DEG': 'particle',
    'DEV': 'particle',
    'DER': 'particle',
    'AS': 'particle',
    'SP': 'particle',
    'ETC': 'particle',
    'MSP': 'particle',
    'IJ': 'interjection',
    'ON': 'onomatopoeia',
    'JJ': 'other noun-modifier',
    'PU': 'punctuation',
    'FW': 'foreign word',
    'OTHER': 'others'
}

# Function to convert text to pinyin
def text_to_pinyin(text: str) -> str:
    words = tokenizer(text)
    result = []
    for word in words:
        py = pinyin(word, style=Style.TONE, heteronym=False)
        result.append(''.join([s[0] for s in py]))
    return ' | '.join(result)

# Function to get POS tags using HanLP
def hanlp_pos_tags(text: str):
    words = tokenizer(text)
    tagged = pos_tagger(words)
    tagged_desc = [pos_dict.get(tag, tag) for tag in tagged]
    return ' | '.join(tagged_desc)

# Function to translate text
def translate_text(text: str, src: str = "zh-cn", dest: str = "en") -> str:
    translation = translator.translate(text, src=src, dest=dest)
    return translation.text

# Function to translate word by word
def translate_tokens(text: str, src: str = "zh-cn", dest: str = "en") -> str:
    words = tokenizer(text)
    translations = []
    for word in words:
        translated = translator.translate(word, src=src, dest=dest)
        translations.append(translated.text.lower())
    return ' | '.join(translations)

# Colors
BOLD = "\033[1m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[38;5;81m"
GREEN = "\x1b[38;5;49m"
RESET = "\033[0m"

# Get text from command line argument
if len(sys.argv) < 2:
    print("Usage: python script.py <text>")
    sys.exit(1)

# Text parameter
texto = sys.argv[1]

# Print result
print(f"{BOLD}Library{RESET}: hanlp")
print(f"{BOLD}Original{RESET}: {RED}{texto}{RESET}")
print(f"{BOLD}Pinyin{RESET}: {YELLOW}{text_to_pinyin(texto)}{RESET}")
print(f"{BOLD}Tags{RESET}: {YELLOW}{hanlp_pos_tags(texto)}{RESET}")
print(f"{BOLD}Translate{RESET}: {GREEN}{translate_text(texto)}{RESET}")
print(f"{BOLD}Literal{RESET}: {GREEN}{translate_tokens(texto)}{RESET}")