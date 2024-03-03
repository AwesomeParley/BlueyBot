import asyncio
import discord
from discord.ext import tasks
import random
import os
import json
import configparser
import time
from datetime import datetime
from datetime import timedelta
import pytz
import urllib.request #will be used to get images from Blueydle if any
from sys import exit

# Check if the settings file exists, if not create it
def create_default_settings():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'Token': 'Insert Bot Token Here',
        'Owner ID': '0',
        'Seconds to respond': '120',
        'Allow cooperative': 'True',
        'Allow daily': 'False',
        'Command': '!guess',
        'Spoilers': 'False',
        'Reactions': 'True',
        'Allow after images': 'True',
        'Force text only': 'False',
        'Allow image download': 'False',
        'DMs are test mode': 'True'
    }
    with open('settings.txt', 'w') as configfile:
        config.write(configfile)

def create_server_settings():
    # Create the initial server settings dictionary
    server_settings = {
        "image_update_counter": 0,
        "server_ids": [],
        "server_settings": {}
    }
    # Write the initial server settings to a JSON file
    update_server_settings(server_settings)

def update_server_settings(server_settings):
    if not os.path.exists('server_settings.json'):
        with open("server_settings.json", "w") as file:
            json.dump(server_settings, file, indent=4)
    with open("server_settings.json", "r") as file:
        check = json.load(file)
    with open("server_settings.json", "w") as file:
        json.dump(server_settings, file, indent=4)
    with open("server_settings.json", "r") as file:
        server_settings = json.load(file)
    return not check == server_settings

def read_settings():
    config = configparser.ConfigParser()
    config.read('settings.txt')
    settings = {
        'Token': config.get('DEFAULT', 'Token'),
        'Owner ID': config.getint('DEFAULT', 'Owner ID'),
        'Seconds to respond': config.getint('DEFAULT', 'Seconds to respond'),
        'Allow cooperative': config.getboolean('DEFAULT', 'Allow cooperative'),
        'Allow daily': config.getboolean('DEFAULT', 'Allow daily'),
        'Command': config.get('DEFAULT', 'Command'),
        'Spoilers': config.getboolean('DEFAULT', 'Spoilers'),
        'Reactions': config.getboolean('DEFAULT', 'Reactions'),
        'Allow after images': config.getboolean('DEFAULT', 'Allow after images'),
        'Force text only': config.getboolean('DEFAULT', 'Force text only'),
        'Allow image download': config.getboolean('DEFAULT', 'Allow image download'),
        'DMs are test mode': config.getboolean('DEFAULT', 'DMs are test mode')
    }
    return settings

if not os.path.exists('settings.txt'):
    create_default_settings()
if not os.path.exists('server_settings.json'):
    create_server_settings()

#Read settings from settings.txt
settings = read_settings()
token = settings['Token']
ownerID = settings['Owner ID']
seconds_to_respond = settings['Seconds to respond']
cooperative = settings['Allow cooperative']
daily = settings['Allow daily'] 
command = settings['Command']
spoilers = settings['Spoilers']
reactions = settings['Reactions']
forceTextOnly = settings['Force text only']
allowAfterImages = settings['Allow after images']
allowDL = settings['Allow image download']
DMsAreTestMode = settings['DMs are test mode']

#Read settings from server_settings.json
with open("server_settings.json", "r") as file:
    server_settings = json.load(file)

if(token == 'Insert Bot Token Here'):
    print("⚠️ Change \"Insert Bot Token Here\" in setting.txt to your discord bot token before running! ⚠️")
    time.sleep(30) # added this so people using the exe or just running the python on it's own can read the message above.
    exit()
else:
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

def downloadImages(): #try to download any images that have yet to be downloaded from Blueydle (sorry Blueydle owner, I will make it not run often at all.)
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
        print("⚠️ No downloaded images found. Please download them to use Image Mode. ⚠️\nIf you don't plan on using image mode, set \"text only\" mode to True in settings.txt")
        time.sleep(30)
        exit()
    else:
        print("⚠️ No downloaded images found. Please download them to use After Images. ⚠️\nIf you don't plan on using After Images, set \"allow after images\" mode to False in settings.txt")
        time.sleep(30)
        exit()

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
    if not os.path.exists('server_settings.json'):
        time.sleep(10)
    try: #added this in case of (very rare) bot death aka wifi gets disconnected
        dailyMode.start()
    except:
        pass
    try:
        update_server_settings_45_min.start()
    except:
        pass
    if(allowDL):
        try:
            downloadImagesLoop.start()
        except:
            pass

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
    # Allows Owner to update the Server Settings manually via Discord
    if message.content.lower() == "!updatess" or message.content.lower() == "!ssupdate":
        if not message.author.id == ownerID:
            return
        if update_server_settings(server_settings):
            await message.reply("Server settings have been manually updated.")
            print(f"✅🕴️ Server Settings have been manually updated by \"{message.author.name}\".")
        else:
            await message.reply("Server settings already up to date.")
            print(f"❌🕴️ \"{message.author.name}\" tried to update the Server Settings manually but they were already up to date.")
        return

    # Directs the bot users to the bot's GitHub page to make suggestions or report bugs
    if message.content.lower() == "!botsuggest" or message.content.lower() == "!suggestbot":
        await message.reply("Thank You for considering to tell us about a new Feature idea or Reporting a Bug with the bot!\nThe website is: https://github.com/AwesomeParley/BlueyBot/issues")

    # Boring Server Setup that will take ages to program :/
    if message.content == "!setupbot" or message.content == "!botsetup":
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
                defaultMode = 1
                mode = "Image"
            else:
                await ans.reply("Alright! Text Mode it is! Now for the next step!\n\nDo you want to force Text Mode?")
                defaultMode = 2
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
                    forceMode = True
                else:
                    await ans.reply(f"Okay! I will *not* force {mode} Mode.\nNext Step; do you want to enable Daily Mode?")
                    forceMode = False
            else:
                if ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                    await ans.reply(f"Okay! I will force {mode} Mode.\nCongrats! You have set up {client.user.name} in your server!")
                    forceMode = True
                else:
                    await ans.reply(f"Okay! I will *not* force {mode} Mode.\nCongrats! You have set up {client.user.name} in your server!")
                    forceMode = False
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
                serverDaily = True
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
                if ans.content in pytz.all_timezones:
                    timezone = pytz.timezone(ans.content)
                else:
                    i = True
                    while i:
                        await ans.reply(f"Sorry, I couldn't understand you!\nWhat timezone are you in? (e.g., 'EST' for Eastern Standard Time)")
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
                dailyTime = bot_time.strftime("%H:%M")
            else:
                await ans.reply(f"Alright! Daily Mode will be off!\nCongrats! You have set up {client.user.name} in your server!")
                serverDaily = False
        if ownerID == message.author.id:
            await ans.reply(f"Oh wait, <@{message.author.id}>! Since you own this bot, do you want this server to be a test server?")
            ans = await wait_for_message()
            if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                return
            while not(ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on') or ans.content.lower() in ('no', 'n', 'false', 'f', '0', 'disable', 'off')):
                await ans.reply("Sorry, I couldn't understand you!\nDo you want this server to be a test server?\nAccepted answers: \"yes\", \"no\".")
                ans = await wait_for_message()
                if ans == "" or ans.content.lower() == "nvm" or ans.content == command:
                    return
            if ans.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                await ans.reply("Alright! This will be a test server.")
                testServer = True
            else:
                await ans.reply("Alright! This will *not* be a test server.")
                testServer = False
        try:
            server_settings["server_settings"][server_id]["default_mode"] = defaultMode
            del defaultMode
            server_settings["server_settings"][server_id]["force_mode"] = forceMode
            del forceMode
        except:
            pass
        try:
            server_settings["server_settings"][server_id]["daily"] = serverDaily
            del serverDaily
            server_settings["server_settings"][server_id]["daily_time"] = dailyTime
            del dailyTime
        except:
            pass
        try:
            server_settings["server_settings"][server_id]["test_server"] = testServer
            del testServer
        except:
            pass
        update_server_settings(server_settings)
        return

    # Fun Guess Game! 
    if str(message.content).startswith(command):
        z = 0
        x = randEpisode()
        print(x)
        DMs = True
        episode = get_episode(x)
        if (DMs and DMsAreTestMode) or server_settings["server_settings"][str(server_id)]['test_server']:
            print(f"[TEST MODE] Episode ID: {x}")
        y = 1
        while y <= max_attempts:
            if z == 0:
                botTyping = message.channel.typing()
                if not forceTextOnly: # Image Mode
                    filename = f'images\\{x}_{y}.jpg' # Format the filename string with x and y
                    with open(filename, 'rb') as f:
                        if spoilers: 
                            file = discord.File(f, filename='SPOILER_nice_try.jpg') # Named "SPOILER_nice_try.jpg" so that the smart people get trolled, and the image is set as a spoiler.
                        else:
                            file = discord.File(f, filename='nice_try.jpg') # Named "nice_try.jpg" so that the smart people get trolled.
                    if not max_attempts == 1:
                        if cooperative and message.content.endswith("coop"):
                            if not y*2+z-2 == 1:
                                guess_amount = f'You have used {y*2+z-2}/{max_attempts*2} guesses. '
                            else:
                                guess_amount = f'You have used 1/{max_attempts*2} guess. '
                        else:
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
                        if cooperative and message.content.endswith("coop"):
                            guess_amount = f'You are on guess {y*2+z}/{max_attempts*2}. '
                        else:
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
                await message.channel.send(f"Sorry, you took too long to guess! (limit is {seconds_to_respond} seconds.)\nThis episode of Bluey was called *{episode}*")
                return

            if any(guess.content.startswith(item) for item in [command, '!serversetup', '!setupserver']): #checks if they sent a command instead
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

def randEpisode():
    if not forceTextOnly:
        x = random.randint(1, episode_amount)
        while x == 44 or x == 45: #Will fix eventually, but for right now, just don't use those
            x = random.randint(1, episode_amount)
        return x
    else:
        return random.randint(1, 151) #There are 151 episodes avalible currently.

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
    "server_name": guild.name,
    "server_command": "!guess",
    "default_mode": 1,
    "force_mode": False,
    "daily": False,
    "daily_time": "14:00",
    "observe_daylight_time": True,
    "daily_channel": 1,
    "daily_guess_amount": 3,
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

#checks if it's time for a daily mode in any server
@tasks.loop(seconds=60)
async def dailyMode():
    if daily:
        now = datetime.utcnow()
        for server in client.guilds: 
            if not os.path.exists('server_settings.json'):
                time.sleep(5)
            utc_time = datetime.strptime(server_settings["server_settings"][str(server.id)]['daily_time'], "%H:%M")
            if str(server.id) in server_settings["server_settings"] and server_settings["server_settings"][str(server.id)]["observe_daylight_time"]:
                if str(server.id) in server_settings["server_settings"] and server_settings["server_settings"][str(server.id)]["daily"] and utc_time.hour == (now + timedelta(hours=1)).hour and utc_time.minute == now.minute:
                    await dailyModeRun(str(server.id))
            else:
                if str(server.id) in server_settings["server_settings"] and server_settings["server_settings"][str(server.id)]["daily"] and utc_time.hour == now.hour and utc_time.minute == now.minute:
                    await dailyModeRun(str(server.id))

@tasks.loop(hours=24)
async def downloadImagesLoop():
    print("Checking for new images...")
    downloadImages()

@tasks.loop(minutes=45)
async def update_server_settings_45_min():
    wasUpdateSS = update_server_settings(server_settings) 
    if wasUpdateSS:
        print("✅ Updated Server Settings")

#run a daily mode in a server
async def dailyModeRun(serverID):
    channel = client.get_channel(server_settings['server_settings'][serverID]['daily_channel'])
    x = randEpisode()
    y = 1
    episode = get_episode(x)
    guess_amount = int(server_settings["server_settings"][str(serverID)]['daily_guess_amount'])
    if guess_amount > 1:
        add_es = 'es'
    else:
        add_es = ''
    if not forceTextOnly: #Image Mode
        z = 0
        while y <= 5 and z <= 5:
            # get image
            filename = f'images\\{x}_{y}.jpg'
            with open(filename, 'rb') as f:
                if spoilers: 
                    file = discord.File(f, filename='SPOILER_nice_try.jpg') 
                else:
                    file = discord.File(f, filename='nice_try.jpg')
            # send message with image
            if (y == 1 and z == 0):
                message = await channel.send(content = f"# Welocme to Today's Blueydle!\nYour goal is to try and guess the Bluey episode name based on the images below. Each {guess_amount} guess{add_es} we will add another image from the episode to make it easier. Now with that out of the way...\n## Guess the Episode!", file=file)
                del add_es
            elif z == 0:
                await channel.send(f"## You have used up {(y-1)*guess_amount}/{guess_amount*5} guesses so far!\nSince that's a muliple of {guess_amount}, here's a new image!", file=file)
            # get return message
            def check(m):
                return m.channel == channel and not(m.author == client.user)
            try:
                guess = await client.wait_for('message', check=check, timeout=86395)
            except asyncio.TimeoutError:
                await message.channel.send(f"Sorry, everyone took too long to guess! Today's episode of Bluey was called *{episode}*")
                return
            # check if it's correct
            if guess.content.replace('.', '', -1).replace(' ', '', -1).lower() == episode.replace('.', '', -1).replace(' ', '', -1).lower():
                # if correct, add ✅ reaction and tell player they got it. 
                try:
                    await guess.add_reaction('✅')
                except:
                    print(f"unable to react to {guess.author}\'s message with ✅")
                if allowAfterImages and y < 5:
                    files = []
                    for y in range(y+1, 6):
                        file_path = f'images\\{x}_{y}.jpg'
                        files.append(discord.File(file_path))
                    await guess.reply(content = f"## Wackadoo! You got it <@{guess.author.id}>!\nThis episode of Bluey was called: *{episode}*", files=files)
                else:
                    await guess.reply(f"## Wackadoo! You got it <@{guess.author.id}>!\nThis episode of Bluey was called: *{episode}*")
                return
            else:
                # if not correct add ❌ reaction
                try:
                    await guess.add_reaction('❌')
                except:
                    print(f"unable to react to {guess.author}\'s message with ❌ in a Daily.")
                # check if this is the last guess the player can makex
                if (y)*guess_amount == guess_amount*5 and z+1 == guess_amount:
                    # if it is the last guess the player can make, tell them the answer. 
                    await message.reply(f"## Ah Biscuits!\nThis episode of Bluey was called: *{episode}*")
                    return
                # if it isn't the last guess they can make, add to the counter. 
                if(z+1 == guess_amount):
                    z=0
                    y+=1
                else:
                    z+=1
    else: #Text Mode not even gonna deal with until I get image mode working
            #insert Text mode here
        return

#login to discord as bot
try:
    client.run(token)
except:
    # if login gives an error, tell the user and stop the program after 30 seconds
    print(f"⚠️ Your token \"{token}\" is not valid or there was an error.\nPlease check the Token in \"settings.txt\" and try agian. ⚠️")
    time.sleep(30)
    exit()