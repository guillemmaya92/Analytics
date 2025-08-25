import hanlp
from pypinyin import pinyin, Style
import jieba
import jieba.posseg as pseg
import sys
from googletrans import Translator

# Silenciar mensajes de Jieba
jieba.setLogLevel(20)

# Cargamos el modelo de tokenización
tokenizer = hanlp.load('CTB9_TOK_ELECTRA_BASE')

# POS dictionary in English
POS_DICT_EN = {
    "n": "noun",
    "v": "verb",
    "r": "pronoun",
    "a": "adjective",
    "d": "adverb",
    "m": "numeral",
    "q": "quantifier",
    "p": "preposition",
    "c": "conjunction",
    "u": "particle",
    "xc": "other",
    "w": "punctuation",
    "y": "modal particle",
    "x": "non-morpheme character",
    "vn": "verbal noun",
    "vg": "verb morpheme"
}

translator = Translator()

def text_to_pinyin(text: str) -> str:
    words = tokenizer(text)
    result = []
    for word in words:
        py = pinyin(word, style=Style.TONE, heteronym=False)
        result.append(''.join([s[0] for s in py]))
    return ' | '.join(result)

def jieba_pos_on_hanlp_words(text: str):
    words = tokenizer(text)
    pos_list = []
    full_names = []
    for word in words:
        for w in pseg.cut(word):
            pos_list.append(w.flag)
            full_names.append(POS_DICT_EN.get(w.flag, 'Unknown'))
    return pos_list, full_names

# Take text from PowerShell
if len(sys.argv) > 1:
    texto = " ".join(sys.argv[1:])
    print("Library: hanlp + jieba")
    print("Original:", texto)
    print("Pinyin:", text_to_pinyin(texto))
    
    pos_tags, pos_names = jieba_pos_on_hanlp_words(texto)
    print("POS tags:", ' | '.join(pos_names))
    
    # Traducción del texto completo
    translation = translator.translate(texto, src='zh-cn', dest='en')
    print("Translate:", translation.text)

    # Traducción literal palabra por palabra (en minúsculas)
    words = tokenizer(texto)
    literal_translations = [translator.translate(word, src='zh-cn', dest='en').text.lower() for word in words]
    print("Literal:", " | ".join(literal_translations))

else:
    print("Please pass a Chinese text as argument from PowerShell.")