# BlueyBot
Discord Bot for guessing Bluey Episodes from images and/or descriptions.

This bot is very much inspired by, and based on [Blueydle](https://blueydle.fun/).

## Features
### !guess command
"!guess" is the default command which can be [changed in the settings](https://github.com/AwesomeParley/BlueyBot#settings) if you dislike it, or if it conflicts with other commands other bots may have. There are currently 2 modes for the !guess command; [Image Mode](https://github.com/AwesomeParley/BlueyBot#image-mode) and [Text Mode](https://github.com/AwesomeParley/BlueyBot#text-mode). These modes can be [changed in the settings](https://github.com/AwesomeParley/BlueyBot#settings) as well via the option "Text only". 

Although more modes may be added in future updates, there are no plans or ideas for any currently. If you have any ideas for new modes, please [open an issue](https://github.com/AwesomeParley/BlueyBot/issues).
#### Image Mode
Allows users to see a screenshot from an episode then guess the episode based on it. 
You have a default of 120 seconds per image to guess what the episode is from; if you fail, you get another image from the same episode to guess. 
Each image should give you more info about the episode until the very last one where it will be very obvious.
You get 5 guesses, and if you fail all 5, it tells you what episode the image is from.
Also, if ```allow after images = True``` in [```settings.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/settings.txt), the bot will show all the remaining images, if any, after you win. 

<p float="center">
  <img alt="Gif representing image mode without after images" src="https://github.com/AwesomeParley/BlueyBot/assets/90052285/9b31f0b2-651e-486b-ada0-492e819a372b" width=49% height=49%>
  <img alt="Image representing image mode with after images" src="https://github.com/AwesomeParley/BlueyBot/assets/90052285/389e4595-39f0-4b9d-93e4-c5770f1677d4" width=49% height=49%>
</p>

#### Text Mode 
Allows users to read a description of an episode and guess the episode based on it. 
You have a default of 120 seconds per guess to figure out what the episode is; if you fail, you get another guess.
You get 2 guesses, and if you fail both, it tells you what the episode is. 
This mode is a lot less fun in my personal opinion, but if you can't use images due to bandwidth limitations, this would be the recommended way to go.
Also, if ```allow after images = True``` in [```settings.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/settings.txt), the bot will show the 5th image, if it has it, after you win.

<p float="center">
<img src="https://github.com/AwesomeParley/BlueyBot/assets/90052285/de6cf5ca-5dd9-4688-9a45-8524ce123a04" width=49% height=49%>
<img src="https://github.com/AwesomeParley/BlueyBot/assets/90052285/70b92504-edab-4cdb-b2af-67c5f186cee2" width=49% height=49%>
</p>

### Settings
Allows the owner to set settings for the bot. Setting include:
- Time per guess (default is 120 seconds)
- Guess command (default is "!guess")
- Reactions (default is True)
- All text and images as spoilers (default is False)
- Allow After Images (default is True)
- Force Text Only mode (default is False)
- Allow image download from [Blueydle](https://blueydle.fun/) (default is False)

All of these can be found in [```settings.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/settings.txt)

### Extra features
Here are some extra features that are too small to list or don't really matter to most users
- Due to the bot not using slash commands, it's possible to guess episodes via DMs.
- If you are so inclined to, you can absolutely change the images, descriptions, and answers to whatever you want using the images folder, [```episodes.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/episodes.txt), [```episodes_in_order.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/episodes_in_order.txt), and [```episode_descriptions.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/episode_descriptions.txt).

## Current Limitations
Some limitations that I can fix, but as of now are not important:
- You can get the same episode multiple times in a row due to the nature of randomness
- No slash commands
- No leaderboard capabilities
- Only 87 (soon 91) different image episodes (all are from on [Blueydle](https://blueydle.fun/).)
- Can't currently do any server specific stuff
These limitations are only in the current version, and are not a representation of what is not possible.

## Future Features
Here's some planned features:
- Server settings that can be edited by admins/owners of each server through commands [working on]
- Daily mode (Server-wide guessing at a specified time set by admins) [working on]
- Slash commands [confused by]
- Image Mode updates from [Blueydle](https://blueydle.fun/) [working on]
- Servers and Users can choose between [Image](https://github.com/AwesomeParley/BlueyBot#image-mode) and [Text Only](https://github.com/AwesomeParley/BlueyBot#text-mode) modes [working on]
- Settings explanations inside [```settings.txt```](https://github.com/AwesomeParley/BlueyBot/blob/main/settings.txt) [working on]
- Much more (TBD)
