# BlueyBot
Discord Bot for guessing Bluey Episodes from images and descriptions.

This bot is very much inspired by and based on [Blueydle](https://blueydle.fun/).

## Features
### !guess command
This is the default command. This command can be [changed in the settings](https://github.com/AwesomeParley/BlueyBot/edit/main/README.md#settings).
#### Image Mode
Allows users to see a screenshot from an episode and guess the episode based on it. 
You have a default of 120 seconds per image to guess what the episode is from; if you fail, you get another image from the same episode to guess. 
Each image should give you more info about the episode until the very last one where it will be very obvious.
You get 5 guesses, and if you fail all 5, it tells you what episode the image is from.

<img src="https://github.com/AwesomeParley/BlueyBot/assets/90052285/9b31f0b2-651e-486b-ada0-492e819a372b" width=50% height=50%>

#### Text Mode 
Allows users to read a description of an episode and guess the episode based on it. 
You have a default of 120 seconds per description to guess what the episode is; if you fail, you get another guess.
You get 2 guesses, and if you fail both, it tells you what the episode is. 
This mode is a lot less fun in my opinion, but if you can't use images due to bandwidth limitations, this would be the recommended way to go.

<img src="https://github.com/AwesomeParley/BlueyBot/assets/90052285/6153986d-84a3-4340-be47-863c8acf5657" width=50% height=50%>

### Settings
Allows the owner to set settings for the bot. Setting include:
- time per guess (default is 120 seconds)
- the guess command (default is "!guess")
- if reactions show up (default is True)
- if you want to set all text and images as spoilers (default is False)
- if you want Text Only mode (default is False)

All of these can be found in settings.txt
## Current Limitations
Some limitations that I can fix, but as of now are not important:
- You can get the same episode multiple times in a row due to the nature of randomness
- No slash commands
- No leaderboard capabilities
- Only 87 different image episodes (all are from on [Blueydle](https://blueydle.fun/).)
- Server specific stuff
## Future Features
Here's some planned features:
- Server settings that can be edited by admins/owners of each server through commands
- Daily mode (Server-wide guessing at a specified time set by admins)
- Slash commands
- Much more (TBD)
