from chatterbot import ChatBot

chatbot = ChatBot('MonChatBot')
with open('File.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
for line in lines:
    question, reponse = line.split(';')
    chatbot.train([question, reponse])
while True:
    user_input = input("Vous: ")
    response = chatbot.get_response(user_input)
    print("ChatBot:", response)
