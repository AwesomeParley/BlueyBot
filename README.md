# BlueyBot
Discord Bot for guessing Bluey Episodes from images and/or descriptions.

This bot is very much inspired by, and based on [Blueydle](https://blueydle.fun/).

## Features
### !guess command
"!guess" is the default command which can be [changed in the settings](https://github.com/AwesomeParley/BlueyBot#settings) if you dislike it, or if it conflicts with other commands other bots may have. There are currently 2 modes for the !guess command; [Image Mode](https://github.com/AwesomeParley/BlueyBot#image-mode) and [Text Mode](https://github.com/AwesomeParley/BlueyBot#text-mode). These modes are [changed in the settings](https://github.com/AwesomeParley/BlueyBot#settings)  as well via the option "Text only". 

Although more modes may be added in future updates, there are no plans or ideas for any currently. If you have any ideas for new modes, please [open an issue](https://github.com/AwesomeParley/BlueyBot/issues).
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
- Can't currently do any server specific stuff
These limitations are only in the current version, and are not a representation of what is not possible.
## Future Features
Here's some planned features:
- Server settings that can be edited by admins/owners of each server through commands [working on]
- Daily mode (Server-wide guessing at a specified time set by admins) [working on]
- Slash commands [confused by, but working on]
- Image Mode updates from [Blueydle](https://blueydle.fun/) [working on]
- Servers and Users can choose between [Image](https://github.com/AwesomeParley/BlueyBot#image-mode) and [Text Only](https://github.com/AwesomeParley/BlueyBot#text-mode) modes [working on]
- Settings explanations inside settings.txt [working on]
- Much more (TBD)
