from openai import OpenAI
import sys
import re

# Create a openrouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Get text from command line argument
if len(sys.argv) < 2:
    print("Usage: python script.py <text>")
    sys.exit(1)

# Text parameter
user_prompt = sys.argv[1]


# Send prompt to DeepSeek model with a translator instruction
completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324",
    messages=[
        {"role": "system", "content": (
            "You are a professional Chinese translation assistant. "
            "Always translate any input into standard, formal Chinese suitable for foreign learners. "
            "Prioritize clear, textbook-style expressions, keeping the translation as close as possible to the original meaning. "
            "Avoid colloquial or regional variations. "
            "When segmenting Chinese, follow the conventions of the HanLP library: "
            "segment text strictly at the word level, keep multi-character compounds intact "
            "(e.g. 哪里, 今天, 学校, 学生), and treat punctuation marks (。 ， ！ ？ etc.) as separate tokens. "
            "Strictly respond in the following format:\n\n"
            "Original: <full Chinese sentence>\n"
            "Chars: <HanLP-style tokens separated by ' | '>\n"
            "Pinyin: <use pinyin with tone mark accents, write each full word as one unit (e.g. 哪里 = nǎlǐ), separate words with ' | ', and write punctuation as itself>\n"
            "Tags: <POS tags (only description) separated by |, include 'punctuation' for punctuation tokens>\n"
            "Translate: <English translation>\n"
            "Literal: <translate each Chinese character into its English meaning word by word, keeping punctuation markers translated as well>"
        )},
        {"role": "user", "content": user_prompt}
    ]
)

text = completion.choices[0].message.content


# Colores ANSI para cada sección
COLORS = {
    "Original": "\033[91m",
    "Chars": "\033[91m",
    "Pinyin": "\033[93m",
    "Tags": "\033[93m",
    "Translate": "\x1b[38;5;49m",
    "Literal": "\x1b[38;5;49m", 
}
RESET = "\033[0m"

# Función para colorear el contenido de cada sección
def color_sections(text):
    for key, color in COLORS.items():
        # Buscar la sección y colorear todo lo que sigue hasta la próxima etiqueta o el final
        pattern = rf"{key}:\s*(.*?)(?=(\n(?:Original|Chars|Pinyin|Tags|Translate|Literal):)|$)"
        text = re.sub(pattern, lambda m: f"{key}: {color}{m.group(1)}{RESET}", text, flags=re.DOTALL)
    return text

# Mostrar resultado coloreado
print(color_sections(text))