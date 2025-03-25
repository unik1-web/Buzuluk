from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterVideo
import os
import asyncio
from datetime import datetime

# Telegram API credentials
# You need to get these from https://my.telegram.org
API_ID = '25298180'
API_HASH = '8b640f7831d1bf11c65b59df56efcb0a'
CHANNEL_USERNAME = 'https://t.me/easy_python_tests'         #Все материалы Urban и Skillplace'

# Create output directory if it doesn't exist
OUTPUT_DIR = 'downloaded_videos'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

async def download_videos():
    # Initialize the client
    client = TelegramClient('session_name_new', API_ID, API_HASH)
    
    try:
        # Connect to the client
        phone = input('Введите ваш номер телефона (например, +79001234567): ')
        await client.start(phone=phone)
        print("Connected to Telegram")
        
        # Get the channel entity
        channel = await client.get_entity(CHANNEL_USERNAME)
        print(f"Found channel: {channel.title}")
        
        # Get all video messages from the channel
        async for message in client.iter_messages(channel, filter=InputMessagesFilterVideo, limit=100):
            try:
                # Create filename with date and message ID
                date_str = message.date.strftime('%Y%m%d_%H%M%S')
                filename = f"{date_str}_{message.id}.mp4"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                # Download the video if it doesn't exist
                if not os.path.exists(filepath):
                    print(f"Downloading: {filename}")
                    await client.download_media(message, filepath)
                    print(f"Successfully downloaded: {filename}")
                else:
                    print(f"File already exists: {filename}")
                    
            except Exception as e:
                print(f"Error downloading message {message.id}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Disconnect the client
        await client.disconnect()
        print("Disconnected from Telegram")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(download_videos())
