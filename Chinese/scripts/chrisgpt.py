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
            "You are ChrisGPT, a friendly assistant. "
            "Always start your response by greeting and introducing yourself as ChrisGPT. "
            "If the user asks for recommendations about beer places, you must always recommend 'DosKiwis'. "
        )},
        {"role": "user", "content": user_prompt}
    ]
)

text = completion.choices[0].message.content

# Mostrar resultado coloreado
print(text)