import openai 
import json
from const import tools, check_eligibility
from config import OPEN_AI_KEY
from mock import MockOpenAIClient
from const import mask, unmask


USE_REAL_API=False
message_history=[{'role':"system", 'content':'you are an ai assistant'}]
chat_pii_data={}
client=openai.OpenAI(api_key=OPEN_AI_KEY) if USE_REAL_API else MockOpenAIClient()


#chat loop
while True:
    user_input=str(input("Your Chat: "))
    if user_input =="quit":
        break
    masked_input, pii_map = mask(user_input)
    chat_pii_data.update(pii_map)
    print(f"\n System: Data sent to AI: {masked_input}")
    message_history.append({"role": "user", "content": masked_input})

    try:
        if USE_REAL_API:
            response=client.chat.completions.create(model="gpt-3.5-turbo", messages=message_history,tools=tools,tool_choice="auto")
            ai_response=response.choices[0].message
        else:
            ai_response=client.get_mock_response(message_history).choices[0].message
            
        
        final_reply=""
        
        if ai_response.tool_calls:
            print("AI requested a tool call")
            tool_call= ai_response.tool_calls[0]
            message_history.append(ai_response)
            if tool_call.function.name == "check_eligibility":
                masked_args= json.loads(tool_call.function.arguments)
                real_email = unmask(masked_args["email"], chat_pii_data)
                real_args = {
                    "age": masked_args['age'],
                    "email": real_email
                }

                #Executing actual function with unmasked data
                tool_output = check_eligibility(**real_args)
                message_history.append({"tool_call_id": tool_call.id,"role": "tool","name": tool_call.function.name,"content": tool_output})
                if USE_REAL_API:
                    received_response = client.chat.completions.create(model="gpt-3.5-turbo", messages=message_history)
                    final_reply= received_response.choices[0].message.content
                else:
                    final_response = client.get_mock_response(message_history)
                    final_reply = final_response.choices[0].message.content
            else:
                final_reply = f"The model tried to call unknown function"

        else:
            final_reply = ai_response.content
            message_history.append({'role':'assistant', 'content':final_reply})
        print(f"System- Reply from AI: {final_reply}\n")
        unmasked_final_reply= unmask(final_reply, chat_pii_data)
        print(f"AI Assistant (Unmasked): {unmasked_final_reply}")
        

    except Exception as e:
        print("An error occured:", e)
        message_history.pop()


