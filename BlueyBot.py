import asyncio
import discord
from discord import app_commands #will use when ready to add slash commands
import random
import os
import json
import configparser
import time #will be used for daily
from datetime import datetime #will be used for daily as well
import pytz
import urllib.request #will be used to get images from Blueydle if any
from sys import exit

# Check if the settings file exists, if not create it
def create_default_settings():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'Token': 'Insert Bot Token Here',
        'Seconds to respond': '120',
        'Allow cooperative': 'True',
        'Allow daily': 'False',
        'Command': '!guess',
        'Spoilers': 'False',
        'Reactions': 'True',
        'Allow after images': 'True',
        'Force text only': 'False',
        'Allow image download': 'False'
    }
    with open('settings.txt', 'w') as configfile:
        config.write(configfile)

def update_server_settings(server_settings):
    with open("server_settings.json", "w") as file:
        json.dump(server_settings, file, indent=4)

def create_server_settings():
    # Create the initial server settings dictionary
    server_settings = {
        "image_update_counter": 0,
        "server_ids": [],
        "server_settings": {}
    }
    # Write the initial server settings to a JSON file
    update_server_settings(server_settings)

def read_settings():
    config = configparser.ConfigParser()
    config.read('settings.txt')
    settings = {
        'Token': config.get('DEFAULT', 'Token'),
        'Seconds to respond': config.getint('DEFAULT', 'Seconds to respond'),
        'Allow cooperative': config.getboolean('DEFAULT', 'Allow cooperative'),
        'Allow daily': config.getboolean('DEFAULT', 'Allow daily'),
        'Command': config.get('DEFAULT', 'Command'),
        'Spoilers': config.getboolean('DEFAULT', 'Spoilers'),
        'Reactions': config.getboolean('DEFAULT', 'Reactions'),
        'Allow after images': config.getboolean('DEFAULT', 'Allow after images'),
        'Force text only': config.getboolean('DEFAULT', 'Force text only'),
        'Allow image download': config.getboolean('DEFAULT', 'Allow image download')
    }
    return settings

if not os.path.exists('settings.txt'):
    create_default_settings()
if not os.path.exists('server_settings.json'):
    create_server_settings()

#Read settings from settings.txt
settings = read_settings()
token = settings['Token']
seconds_to_respond = settings['Seconds to respond']
cooperative = settings['Allow cooperative']
daily = settings['Allow daily'] #To Be Implemented
command = settings['Command']
spoilers = settings['Spoilers']
reactions = settings['Reactions']
forceTextOnly = settings['Force text only']
allowAfterImages = settings['Allow after images']
allowDL = settings['Allow image download']

#Read settings from server_settings.json
with open("server_settings.json", "r") as file:
    server_settings = json.load(file)
if server_settings["image_update_counter"] == 0:
    allowImageUpdate = True
else:
    allowImageUpdate = False
    if server_settings["image_update_counter"] == 10:
        server_settings["image_update_counter"] = 0
    else:
        server_settings["image_update_counter"] += 1
        update_server_settings(server_settings)

if(token == 'Insert Bot Token Here'):
    print("Change \"Insert Bot Token Here\" in setting.txt to your discord bot token before running!")
    time.sleep(30) # added this so people using the exe or just running the python on it's own can read the message above.
    exit()
else:
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

if (not forceTextOnly) or allowAfterImages:
    # Get a list of all files in the directory
    files = os.listdir("./images")
    # Filter the list to only include files that match the naming pattern
    image_files = [file for file in files if file.endswith("_1.jpg")]
    # Sort the image files based on the increasing number after "_1"
    sorted_files = sorted(image_files, key=lambda x: int(x.split("_")[0]))
    # Check the last image in the sorted list
    if sorted_files:
        episode_amount = int(sorted_files[-1].split("_")[0])
    elif not forceTextOnly:
        print("No downloaded images found. Please download them to use Image Mode.\nIf you don't plan on using image mode, set \"text only\" mode to True in settings.txt.")
        time.sleep(30)
        exit()
    else:
        print("No downloaded images found. Please download them to use After Images.\nIf you don't plan on using After Images, set \"allow after images\" mode to False in settings.txt.")
        time.sleep(30)
        exit()
    if (allowDL and allowImageUpdate) or (allowDL and (datetime.today().weekday() == 5)):
        #try to download any images that have yet to be downloaded from Blueydle (sorry Blueydle owner, I will make it not run often at all.)
        failDLCount = 0
        x = episode_amount+1
        while failDLCount < 7:
            url = f"https://images.blueydle.fun/{x}/1.jpg"
            filename = f"images\\{x}_1.jpg"
            try:
                urllib.request.urlretrieve(url, filename)
                print(f"Downloaded {filename}")
                failDLCount = 0
                for y in range(2, 6):
                    url = f"https://images.blueydle.fun/{x}/{y}.jpg"
                    filename = f"images\\{x}_{y}.jpg"
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
        server_settings["image_update_counter"] += 1
        update_server_settings(server_settings)

if not forceTextOnly:
    episodes_file = "episodes.txt"
    max_attempts = 5 #Only change if you want to use your own images, and you have a different number of them.
else:
    episodes_file = "episodes_in_order.txt"
    max_attempts = 2 #Only change if you want to use your own text or you want to change the number of attempts.

@client.event
async def on_ready():
    print('Logged in as {0.user} and ready for some Bluey episode guessing Action.'.format(client))
    get_servers()

async def on_guild_join(guild):
    print(f'Joined a new guild: {guild.name} (ID: {guild.id})')
    add_server(guild)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    def wait_for_message():
        def check(m): # checks if the message was sent by the same person and in the same channel
                return m.author == message.author and m.channel == message.channel
        try: # wait for a message in that same channel by that same person. 
            return client.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            message.channel.send(f"Sorry, you took too long to answer! (limit is 120 seconds.)\ncanceling...")
            return ""
    # Boring Server Setup that will take ages to program :/
    if message.content == "!setupserver" or message.content == "!serversetup":
        try:
            server_id = str(message.guild.id)
        except:
            await message.reply("You aren't in a server!")
            return
        if not(daily or not forceTextOnly):
            return
        if not message.author.guild_permissions.administrator:
            return
        if not message.guild.id in server_settings["server_ids"]:
            add_server(message.guild)
        if forceTextOnly == False:
            await message.reply("Alright! So the first step of setting up the server is picking the default mode!\nAvalible modes include Image Mode and Text Mode.\nYou can always type \"nvm\" to stop.")
            ans = await wait_for_message()
            if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                return
            while not (ans.content.lower() == ("Image Mode").lower() or ans.content.lower() == ('Text Mode').lower()):
                await ans.reply("Sorry, I couldn't understand you!\nWhat default mode do you want? Image Mode or Text Mode?")
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
            if ans.content.lower() == ("Image Mode").lower():
                await ans.reply("Alright! Image Mode it is! Now for the next step!\n\nDo you want to force Image Mode?")
                server_settings["server_settings"][server_id]["default_mode"] = 1
                mode = "Image"
            else:
                await ans.reply("Alright! Text Mode it is! Now for the next step!\n\nDo you want to force Text Mode?")
                server_settings["server_settings"][server_id]["default_mode"] = 2
                mode = "Text"
            ans = await wait_for_message()
            if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                return
            while not(ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on') or ans.content.lower() in ('no', 'n', 'false', 'f', '0', 'disable', 'off')):
                await ans.reply(f"Sorry, I couldn't understand you!\nDo you want to force {mode} Mode?\nAccepted answers: \"yes\", \"no\".")
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
            if daily:
                if ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                    await ans.reply(f"Okay! I will force {mode} Mode.\nNext Step; do you want to enable Daily Mode?")
                else:
                    await ans.reply(f"Okay! I will *not* force {mode} Mode.\nNext Step; do you want to enable Daily Mode?")
            else:
                if ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                    await ans.reply(f"Okay! I will force {mode} Mode.\nCongrats! You have set up {client.user.name} in your server!")
                else:
                    await ans.reply(f"Okay! I will *not* force {mode} Mode.\nCongrats! You have set up {client.user.name} in your server!")
        elif daily: 
            await message.reply("Alright! So the first step of setting up the server is picking if you want Daily Mode enabled.\nYou can always type \"nvm\" to stop.")
        if daily:
            ans = await wait_for_message()
            if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                return
            while not(ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on') or ans.content.lower() in ('no', 'n', 'false', 'f', '0', 'disable', 'off')):
                await ans.reply("Sorry, I couldn't understand you!\nDo you want Daily Mode enabled?\nAccepted answers: \"yes\", \"no\".")
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
            if ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                await ans.reply("Alright! Daily Mode will be on! Now for the next step!\n\nWhat timezone are you in? (e.g., 'America/New_York')\nThe follow-up question needs it.")
                server_settings["server_settings"][server_id]["daily"] = True
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
                if ans.content in pytz.all_timezones:
                    timezone = pytz.timezone(ans.content)
                else:
                    i = True
                    while i:
                        await ans.reply(f"Sorry, I couldn't understand you!\nWhat timezone are you in? (e.g., 'America/New_York')")
                        ans = await wait_for_message()
                        if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                            return
                        if ans.content in pytz.all_timezones:
                            timezone = pytz.timezone(ans.content)
                            i = False
                await ans.reply(f"Alright! Your timezone has been set to {timezone.zone}.\nNow, what time do you want Daliy Mode to happen each day?\n(format 'HH:MM' or 'HH:MM AM/PM')")
                time_formats = ["%I:%M %p", "%H:%M"]
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
                for fmt in time_formats:
                    try:
                        time_obj = datetime.strptime(ans.content, fmt)
                        break
                    except:
                        continue
                else:
                    i = True
                    while i:
                        await ans.reply(f"Sorry, I couldn't understand you!\nWhat time do you want Daliy Mode to happen each day? (e.g., '5:15 PM')\n(format 'HH:MM' or 'HH:MM AM/PM')")
                        ans = await wait_for_message()
                        if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                            return
                        for fmt in time_formats:
                            try:
                                time_obj = datetime.strptime(ans.content, fmt)
                                i = False
                                break
                            except:
                                continue
                #convert the time to the bot's local time 
                time_obj = time_obj.replace(tzinfo=timezone)
                await ans.reply(f"Alright! Daily Mode will happen at " + time_obj.strftime("%H:%M")+ " " + timezone.zone + f".\nCongrats! You have set up {client.user.name} in your server!")
                bot_time = time_obj.astimezone(pytz.timezone('Etc/UTC'))
                server_settings["server_settings"][server_id]["daily_time"] = bot_time.strftime("%H:%M")
            else:
                await ans.reply(f"Alright! Daily Mode will be off!\nCongrats! You have set up {client.user.name} in your server!")
                server_settings["server_settings"][server_id]["daily"] = False
                
        update_server_settings(server_settings)
        return

    # Fun Guess Game! 
    if str(message.content).startswith(command):
        z = 0
        if not forceTextOnly:
            x = random.randint(1, episode_amount)
            while x == 44 or x == 45: #Will fix eventually, but for right now, just don't use those
                x = random.randint(1, 87)
        else:
            x = random.randint(1, 147) #There are 147 episodes avalible currently.
        y = 1
        while y <= max_attempts:
            episode = get_episode(x)
            if z == 0:
                if not forceTextOnly: # Image Mode
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
                if cooperative and message.content.endswith("coop"):
                    return m.channel == message.channel
                else:
                    return m.author == message.author and m.channel == message.channel
            
            try: # wait for a message in that same channel by that same person. 
                guess = await client.wait_for('message', check=check, timeout=seconds_to_respond)
            except asyncio.TimeoutError:
                await message.channel.send(f"Sorry, you took too long to guess! (limit is {seconds_to_respond} seconds.)\nThis episode of bluey was called *{episode}*")
                return

            if guess.content == command: #checks if they sent a command instead
                return
            elif guess.content.replace('.', '', -1).replace(' ', '', -1).lower() == episode.replace('.', '', -1).replace(' ', '', -1).lower(): # checks if they guessed right
                if reactions:
                    try:
                        await guess.add_reaction('✅')
                    except:
                        print(f"unable to react to {guess.author}\'s message with ✅")
                if allowAfterImages and y < max_attempts and not forceTextOnly:
                    files = []
                    for y in range(y+1, max_attempts+1):
                        file_path = f'images\\{x}_{y}.jpg'
                        files.append(discord.File(file_path))
                    await guess.reply(content = f"**Wackadoo!** You got it!\nThis episode of Bluey was called: *{episode}*", files=files)
                elif forceTextOnly and allowAfterImages:
                    episode_line = find_line_number("episodes.txt", episode)
                    print(episode_line)
                    try:
                        file = discord.File(f'images\\{episode_line}_5.jpg')
                        await guess.reply(content = f"**Wackadoo!** You got it!\nThis episode of Bluey was called: *{episode}*", file=file)
                    except:
                        await guess.reply(f"**Wackadoo!** You got it!\nThis episode of Bluey was called: *{episode}*")
                else:
                    await guess.reply(f"**Wackadoo!** You got it!\nThis episode of Bluey was called: *{episode}*")
                return
            elif reactions:
                try:
                    await guess.add_reaction('❌')
                except:
                    print(f"unable to react to {guess.author}\'s message with ❌")
            if cooperative and message.content.endswith("coop"):
                if z == 1:
                    y +=1
                    z = 0
                else:
                    z += 1
            else:
                y += 1
        if forceTextOnly and allowAfterImages:
            episode_line = find_line_number("episodes.txt", episode)
            try:
                file = discord.File(f'images\\{episode_line}_5.jpg')
                await guess.reply(content = f"**Ah Biscuits!**\nThis episode of Bluey was called: *{episode}*", file=file)
            except:
                await guess.reply(f"**Ah Biscuits!**\nThis episode of Bluey was called: *{episode}*")
        else:
            await message.reply(f"**Ah Biscuits!**\nThis episode of Bluey was called: *{episode}*")
        return

# gets the episode name
def get_episode(x):
    with open(episodes_file) as f:
        episodes = f.readlines()
    episode = episodes[x-1] if len(episodes) >= x else None
    return episode.strip() if episode else None

#Checks if each server is in the list. If it's not, it adds it. 
def get_servers():
    for guild in client.guilds: 
        if not guild.id in server_settings["server_ids"]:
            add_server(guild)
        else: 
            print(guild.name + " (" + str(guild.id) + ") already in list.")

# add server to server_settings.json
def add_server(guild):
    server_settings["server_ids"].append(guild.id)
    print(guild.name + " (" + str(guild.id) + ") added to the list.")
    new_server_settings = {
    "server_command": "!guess",
    "default_mode": 1,
    "force_mode": False,
    "daily": False,
    "daily_time": "14:00",
    "daily_channel": 1,
    "allow_cooperative_mode": True,
    "test_server": False
    }
    server_settings["server_settings"][guild.id] = new_server_settings
    update_server_settings(server_settings) 

def find_line_number(filename, search_string):
    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip() == search_string:
                return line_number
    return -1

try:
    client.run(token)
except:
    print(f"Your token \"{token}\" is not valid or there was an error.\nPlease check the Token in \"settings.txt\" and try agian.")
    time.sleep(30)
    exit()