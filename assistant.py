from openai import OpenAI

client = OpenAI(api_key='sk-proj-h0c2oGEfefX10VuPKsxUT3BlbkFJCibBAMprWdCo2oGdk0FV')

response = client.chat.completions.create(model="gpt-3.5-turbo",
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a poem about the ocean."}
])

print(response.choices[0].message.content.strip())