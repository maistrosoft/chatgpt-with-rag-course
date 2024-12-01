from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from datetime import datetime

def getCompletionFromMessages(messages, 
                                 model="gpt-4o-mini", 
                                 temperature=0, 
                                 max_tokens=2000):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

def collectMessages(prompt):
    context.append({'role':'user', 'content':f"{prompt}"})
    response = getCompletionFromMessages(context)
    context.append({'role':'assistant', 'content':f"{response}"})
    # print("###########  Context  ############")
    # print(context)
    # print("##################################")
    return response

def printOrder():
    messages =  context.copy()
    t = datetime.now().strftime("%m/%d/%Y")
    messages.append(
        {
            'role':'system', 'content':"""create a json summary of the previous food order. Itemize the price for each item\
                                            The fields should be \
                                            1) Name of the restaurant \
                                            2) Date:""" + t + """
                                            3) List of items with quantity and total price for each line item \
                                            4) Total price for the entire order \
                                            For example, your response should look like this: \
                                            { "restaurant": "Bright and Early Restaurant", "date": "01/01/2024", "items": [ { "name": "Latte", "quantity": 2, "price": 10.00 }, { "name": "Croissant", "quantity": 1, "price": 3.00 } ], "tax" : 0.70, "tip": 3.00, "total": 13.00 }
                                        """
        },    
    )
    response = getCompletionFromMessages(messages, temperature=0)
    print(response)

client = OpenAI()

system_message = f"""
You are a waiter in the The Bright and Early Coffee Shop.  \
You should list the menu of items shown here and take a customer's order.  \
Espresso - $5.00, Latte $10.00, Sandwich $7.50, Bagels $2.00 each, Croissant $3.00 each.  \
After the customer completes the order you should list it again to verify.  \
When they ask for the bill you should generate a bill for their order. \
Include the tax (7%), tip (20%) and the total price \
If the user did not order anything, ask them to order something \
If the user asks for the menu, you should list the menu items.
"""

context = [ 
    {'role':'system', 'content': system_message}
]

botResponse = """
Hi, I'm the order bot at The Bright and Early Coffee. How can I help you? :
(Type 'bye' or 'end' to end the conversation)\n
"""
while True:
    userInput = input(botResponse)
    if userInput.lower() == "end" or userInput.lower() == "bye":
        botResponse = collectMessages(userInput) + " : \n"
        printOrder()
        break
    else:
        botResponse = collectMessages(userInput) + " : \n"
        continue

