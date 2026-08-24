import os
from litellm import completion

key = os.environ.get("OPENAI_API_KEY")
print(f"Key found: {'yes' if key else 'NO KEY SET'}")

resp = completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Reply with just: ok"}],
    api_key=key,
    max_tokens=10,
)
print("Response:", resp.choices[0].message.content)
