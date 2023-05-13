import asyncio
import discord
import random
import os
import configparser
from sys import exit

# Check if the settings file exists, if not create it
def create_default_settings():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'Token': 'Insert Bot Token Here',
        'Seconds to respond': '120',
        'Daily': 'False',
        'Command': '!guess',
        'Image spoilers': 'False',
        'Reactions': 'True'
    }
    with open('settings.txt', 'w') as configfile:
        config.write(configfile)

def read_settings():
    config = configparser.ConfigParser()
    config.read('settings.txt')
    settings = {
        'Token': config.get('DEFAULT', 'Token'),
        'Seconds to respond': config.getint('DEFAULT', 'Seconds to respond'),
        'Daily': config.getboolean('DEFAULT', 'Daily'),
        'Command': config.get('DEFAULT', 'Command'),
        'Image spoilers': config.getboolean('DEFAULT', 'Image spoilers'),
        'Reactions': config.getboolean('DEFAULT', 'Reactions'),
    }
    return settings

if not os.path.exists('settings.txt'):
    create_default_settings()

settings = read_settings()
token = settings['Token']
seconds_to_respond = settings['Seconds to respond']
daily = settings['Daily'] #To Be Implemented
command = settings['Command']
spoilers = settings['Image spoilers']
reactions = settings['Reactions']

if(token == 'Insert Bot Token Here'):
    print("change \"Insert Bot Token Here\" in setting.txt to your discord token before running!")
    exit()
else:
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

episodes_file = "episodes.txt"
max_attempts = 5 #Only change if you want to use your own images, and you have a different number of them.

@client.event
async def on_ready():
    print('Logged in as {0.user} and ready for some Bluey episode guessing Action.'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == command:
        x = random.randint(1, 87)
        while x == 44 or x == 45: #Will fix eventually, but for right now, just don't use those
            x = random.randint(1, 87)
        y = 1
        while y <= max_attempts:
            episode = get_episode(x)
            filename = f'images\\{x}_{y}.jpg' # Format the filename string with x and y
            with open(filename, 'rb') as f:
                if spoilers: 
                    file = discord.File(f, filename='SPOILER_nice_try.jpg') # Named "SPOILER_nice_try.jpg" so that the smart people get trolled, and the image is set as a spoiler.
                else:
                    file = discord.File(f, filename='nice_try.jpg') # Named "nice_try.jpg" so that the smart people get trolled.
                await message.reply(f'You are on guess {y}. Guess the episode.', file=file)
            
            def check(m):
                return m.author == message.author and m.channel == message.channel
            
            try:
                guess = await client.wait_for('message', check=check, timeout=seconds_to_respond)
            except asyncio.TimeoutError:
                await message.channel.send(f"Sorry, you took too long to guess! (limit is {seconds_to_respond} seconds.)")
                return
            
            if guess.content.lower() == episode.lower():
                if reactions:
                    try:
                        await guess.add_reaction('✅')
                    except:
                        print(f"unable to react to {guess.author}\'s message with ✅")
                await message.reply(f"**Wackadoo!** You got it!\nThis episode of Bluey was called: *{episode}*")
                return
            elif reactions:
                try:
                    await guess.add_reaction('❌')
                except:
                    print(f"unable to react to {guess.author}\'s message with ❌")
            
            y += 1
        
        await message.reply(f"**Ah Biscuits!**\nThis episode of Bluey was called: *{episode}*")

# gets the episode name
def get_episode(x):
    with open(episodes_file) as f:
        episodes = f.readlines()
    episode = episodes[x-1] if len(episodes) >= x else None
    return episode.strip() if episode else None

client.run(token)