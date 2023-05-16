import asyncio
import discord
import random
import os
import configparser
import time #will be used for daily
import urllib.request #will be used to get images from Blueydle if any
from sys import exit

# Check if the settings file exists, if not create it
def create_default_settings():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'Token': 'Insert Bot Token Here',
        'Seconds to respond': '120',
        'Daily': 'False',
        'Command': '!guess',
        'Spoilers': 'False',
        'Reactions': 'True',
        'Text only': 'False',
        'Allow image download': 'False'
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
        'Spoilers': config.getboolean('DEFAULT', 'Spoilers'),
        'Reactions': config.getboolean('DEFAULT', 'Reactions'),
        'Text only': config.getboolean('DEFAULT', 'Text only'),
        'Allow image download': config.getboolean('DEFAULT', 'Allow image download')
    }
    return settings

if not os.path.exists('settings.txt'):
    create_default_settings()

settings = read_settings()
token = settings['Token']
seconds_to_respond = settings['Seconds to respond']
daily = settings['Daily'] #To Be Implemented
command = settings['Command']
spoilers = settings['Spoilers']
reactions = settings['Reactions']
textOnly = settings['Text only']
allowDL = settings['Allow image download']

if(token == 'Insert Bot Token Here'):
    print("Change \"Insert Bot Token Here\" in setting.txt to your discord bot token before running!")
    time.sleep(30) # added this so people using the exe or just running the python on it's own can read the message above.
    exit()
else:
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

if not textOnly:
    # Get a list of all files in the directory
    files = os.listdir("./images")
    # Filter the list to only include files that match the naming pattern
    image_files = [file for file in files if file.endswith("_1.jpg")]
    # Sort the image files based on the increasing number after "_1"
    sorted_files = sorted(image_files, key=lambda x: int(x.split("_")[0]))
    # Check the last image in the sorted list
    if sorted_files:
        episode_amount = int(sorted_files[-1].split("_")[0])
    else:
        print("No downloaded images found. Please download them to use Image Mode.\nIf you don't plan on using image mode, set \"Text only\" mode to True in settings.txt.")
        time.sleep(30)
        exit()

    if allowDL and False:
        #try to download any images that have yet to be downloaded from Blueydle (sorry Blueydle owner, I will make it not run often at all.)
        failDLCount = 0.0
        x = episode_amount+1
        while failDLCount < 7:
            url = f"https://images.blueydle.fun/{x}/1.jpg"
            filename = f"{x}_1.jpg"
            try:
                urllib.request.urlretrieve(url, filename)
                print(f"Downloaded {filename}")
                failDLCount = 0
                for y in range(2, 6):
                    url = f"https://images.blueydle.fun/{x}/{y}.jpg"
                    filename = f"{x}_{y}.jpg"
                    try:
                        urllib.request.urlretrieve(url, filename)
                        print(f"Downloaded {filename}")
                    except urllib.error.HTTPError:
                        print(f"Failed to download {filename}.")
            except urllib.error.HTTPError:
                failDLCount += 1
                if failDLCount < 7:
                    print(f"Failed to download {filename}. Checking if there are more...")
                else:
                    print(f"Failed to download {filename}.")
            x += 1

if not textOnly:
    episodes_file = "episodes.txt"
    max_attempts = 5 #Only change if you want to use your own images, and you have a different number of them.
else:
    episodes_file = "episodes_in_order.txt"
    max_attempts = 2 #Only change if you want to use your own text, and you have a different number of them.

@client.event
async def on_ready():
    print('Logged in as {0.user} and ready for some Bluey episode guessing Action.'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == command:
        if not textOnly:
            x = random.randint(1, episode_amount)
            while x == 44 or x == 45: #Will fix eventually, but for right now, just don't use those
                x = random.randint(1, 87)
        else:
            x = random.randint(1, 147) #There are 147 episodes avalible currently.
        y = 1
        while y <= max_attempts:
            episode = get_episode(x)
            if not textOnly: # Image Mode
                filename = f'images\\{x}_{y}.jpg' # Format the filename string with x and y
                with open(filename, 'rb') as f:
                    if spoilers: 
                        file = discord.File(f, filename='SPOILER_nice_try.jpg') # Named "SPOILER_nice_try.jpg" so that the smart people get trolled, and the image is set as a spoiler.
                    else:
                        file = discord.File(f, filename='nice_try.jpg') # Named "nice_try.jpg" so that the smart people get trolled.
                if not max_attempts == 1:
                    guess_amount = f'You are on guess {y}/{max_attempts}. '
                else:
                    guess_amount = ''
                await message.reply(f'{guess_amount}Guess the episode.', file=file)
            else: # Text Only Mode
                with open('episode_descriptions.txt') as f: # Get description, then if spoilers are true, then add them to the message
                    episode_descriptions = f.readlines()
                    episode_description = episode_descriptions[x-1] if len(episode_descriptions) >= x else None
                    if spoilers: 
                        description = ("||" + episode_description.strip() + "||" if episode_description else None)
                    else:
                        description = episode_description.strip() if episode_description else None
                if not max_attempts == 1:
                    guess_amount = f'You are on guess {y}/{max_attempts}. '
                else:
                    guess_amount = ''
                if y > 1 and reactions: #instead of sending a whole extra message each time they get it wrong, just edit the previous message the bot sent. Also this only is helpful if reactions are on.
                    await editable.edit(content = f'{guess_amount}Guess the episode:\n\n{description}')
                else:
                    editable = await message.reply(f'{guess_amount}Guess the episode:\n\n{description}')
            
            def check(m): # checks if the message was sent by the same person and in the same channel
                return m.author == message.author and m.channel == message.channel
            
            try: # wait for a message in that same channel by that same person. 
                guess = await client.wait_for('message', check=check, timeout=seconds_to_respond)
            except asyncio.TimeoutError:
                await message.channel.send(f"Sorry, you took too long to guess! (limit is {seconds_to_respond} seconds.)")
                return

            if guess.content == command: #checks if they sent a command instead
                return
            elif guess.content.replace('.', '', -1).lower() == episode.replace('.', '', -1).lower(): # checks if they guessed right
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
        return

# gets the episode name
def get_episode(x):
    with open(episodes_file) as f:
        episodes = f.readlines()
    episode = episodes[x-1] if len(episodes) >= x else None
    return episode.strip() if episode else None

try:
    client.run(token)
except:
    print(f"Your token \"{token}\" is not valid or there was an error.\nPlease check the Token in \"settings.txt\" and try agian.")
    time.sleep(30)
    exit()