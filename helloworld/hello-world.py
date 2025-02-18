from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex cooking instructions with creative flair."},
    {"role": "user", "content": "Compose a humorous poem that explains how to make pizza."}
  ]
)

response = completion.choices[0].message.content

print(response)