# ------------------ Libraries------------------------------
from openai import OpenAI
import sys
import hanlp
from pypinyin import pinyin, Style
from deep_translator import GoogleTranslator

# ------------------ DeepSeek Translation ------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Texto original que quieres traducir
user_prompt = sys.argv[1]

completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324",
    messages=[
        {"role": "system", "content": "You are a professional translation assistant. Always translate any input strictly into Chinese and output nothing else."},
        {"role": "user", "content": user_prompt}
    ]
)

# Guardamos la traducción en 'texto'
texto = completion.choices[0].message.content

# ------------------ HanLP + Pinyin + GoogleTranslator ------------------
# Models
tokenizer = hanlp.load('CTB9_TOK_ELECTRA_BASE')
pos_tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)
translator = GoogleTranslator(source='auto', target='en')

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
def text_to_pinyin(text: str):
    words = tokenizer(text)
    chars_result = []
    pinyin_result = []
    
    for word in words:
        chars_result.append(word)  # caracteres originales
        py = pinyin(word, style=Style.TONE, heteronym=False)
        pinyin_result.append(' '.join([s[0] for s in py]))  # pinyin del token
    
    chars = ' | '.join(chars_result)
    pinyins = ' | '.join(pinyin_result)
    
    return chars, pinyins

# Function to get POS tags using HanLP
def hanlp_pos_tags(text: str):
    words = tokenizer(text)
    tagged = pos_tagger(words)
    tagged_desc = [pos_dict.get(tag, tag) for tag in tagged]
    return ' | '.join(tagged_desc)

# Function to translate text
def translate_text(text: str, src: str = "zh-CN", dest: str = "en") -> str:
    translation = GoogleTranslator(source=src, target=dest).translate(text)
    return translation

# Function to translate word by word
def translate_tokens(text: str, src: str = "zh-CN", dest: str = "en") -> str:
    words = tokenizer(text)
    translations = []
    for word in words:
        translated = GoogleTranslator(source=src, target=dest).translate(word)
        if translated:
            translations.append(translated.lower())
        else:
            translations.append(word)
    return ' | '.join(translations)

# Colors
BOLD = "\033[1m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[38;5;81m"
GREEN = "\x1b[38;5;49m"
RESET = "\033[0m"

# Print result
print(f"{BOLD}Library{RESET}: hanlp")
print(f"{BOLD}Original{RESET}: {RED}{texto}{RESET}")
chars, pinyins = text_to_pinyin(texto)
print(f"{BOLD}Chars{RESET}: {RED}{chars}{RESET}")
print(f"{BOLD}Pinyin{RESET}: {YELLOW}{pinyins}{RESET}")
print(f"{BOLD}Tags{RESET}: {YELLOW}{hanlp_pos_tags(texto)}{RESET}")
print(f"{BOLD}Translate{RESET}: {GREEN}{translate_text(texto)}{RESET}")
print(f"{BOLD}Literal{RESET}: {GREEN}{translate_tokens(texto)}{RESET}")