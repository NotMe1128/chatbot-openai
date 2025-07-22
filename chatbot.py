import openai 
from config import OPEN_AI_KEY

client = openai.OpenAI(api_key=OPEN_AI_KEY)
message_history=[{'role':"system", 'content':'you are an ai assistant'}]

while True:
    input=str(input("Your Chat: "))
    if input =="quit":
        break
    message_history.append({"role": "user", "content": input})

    try:
        response=client.chat.completions.create(model="gpt-2.0", messages=message_history)
        ai_response=response.choices[0].message.content
        print(f"AI assitant: {ai_response}")
        message_history.append({'role':'system', 'content': ai_response})
    except Exception as e:
        print("An error occured:", e)
        message_history.pop()


