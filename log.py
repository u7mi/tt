import sys
from telethon import TelegramClient


api_id = '20001924'  
api_hash = '9638c56b164f36ad63aa485fa581935e'  
phone_number = '+212783626061'

client = TelegramClient('session_name', api_id, api_hash)

async def send_message(message: str):
    await client.start(phone_number)
    
    chat = 'ddos_ss1_bot'  
    
    await client.send_message(chat, message)
    print(f"Message sent: {message}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])  
        with client:
            client.loop.run_until_complete(send_message(message))
    else:
        print("Please provide a message to send.")
