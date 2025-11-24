from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# response = client.chat.completions.create(
#     model="gemma2:9b",
#     messages=[
#         {"role": "user", "content": "Hello, bot!"}
#     ]       
# )

# reply = response.choices[0].message.content
# print(reply)

# Lấy input từ người dùng, nếu như người dùng nhập "exit" thì thoát chương trình
# Từ input, gửi vào prompt của bot cho bot trả lời

while True:
    user_input = input("You: ")
    if user_input == "exit":
        break
    response = client.chat.completions.create(
        model="gemma2:9b",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    reply = response.choices[0].message.content
    print(f"Bot: {reply}")
       