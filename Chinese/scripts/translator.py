from openai import OpenAI
import sys

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
        {"role": "system", "content": "You are a professional chinese translation assistant. Always translate any input into chinese."},
        {"role": "user", "content": user_prompt}
    ]
)

# Colors
RED = "\033[91m"
RESET = "\033[0m"

# Show the translation
print(f"{RED}{completion.choices[0].message.content}{RESET}")