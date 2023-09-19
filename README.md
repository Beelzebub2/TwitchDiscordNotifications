# **TwitchDiscordNotifications**
![Static Badge](https://img.shields.io/badge/Version-v1.5-8ebff1?style=for-the-badge&logo=v)
![Static Badge](https://img.shields.io/badge/Language-python-3776ab?style=for-the-badge&logo=python)
![Static Badge](https://img.shields.io/badge/License-GNU%20GPL%20v3-blue.svg?style=for-the-badge)  
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/S6S8HV2DY)

Get notifications of your favorite streamers on your discord Dm's

## **Important links**
  
Twitch Clientid (Application): https://dev.twitch.tv/console/apps   
**(OAuth redirect link must be "https://twitchapps.com/tokengen/")**  
Twitch OAuth key: https://twitchapps.com/tokengen/  
![OAuth](https://i.imgur.com/fuHBvHK.png)  
Discord bot: https://discord.com/developers/applications/

## Preview  
![notification preview](https://i.imgur.com/my3Z8ks.png)

## **Usage**  
### **Commands**
#### **Must be sent to bot Dm's**  
**Help** - Shows list of commands  
**Watch streamername or streamerlink** - Will get the user id and create a new list if it doesn't exist otherwise it will add the streamer to that users list  
**Unwatch streamername or streamerlink** - Removes the streamer from that user's list  
**Clear** - Deletes all the messages sent by the bot (1per second to avoid being rate limited)  

#### Replit
**It should create the secrets automatically so just change the filler text in there**

## Changes
```diff

v1.5 19/09/2023

+   Made the streamer checker faster
+   Made list image generation faster
+   Fixed some bugs

v1.4 17/09/2023

+   Added invite me command
+   Fixed the local timezone being wrong on replit and for users with different timezone from script host
+   Optimized code and fixed some issues
+   Changed bot data handling from .ini to json
+   Changed the way the bot works to function with commands instead of plain messages
+   Complete rewrite of code

v1.3 02/09/2023

!   Working on better config/data handler
+   Made list command show image of combined streamers profile pictures
+   Added amount of viewers in stream to notifications embed
+   Added stream game to notifications embed
+   Added stream title to notification embed

v1.2 04/07/2023

+   Fixed streamers added after bot initialization not getting checked
+   Made console interface better, showing checking when checking streamer and showing currently streaming streamers
+   Cleaner console
+   Fixed if a streamer was removed from everybodys watchlist, it wouldn't leave the currently streaming list
+   Added stream started at, local  time to notification


v1.1 03/07/2023

+   Added option to use watch with streamername or streamer link
+   Made the notification embeds prettier
+   Added clear command to delete all notifications sent by the bot

v1.0 02/07/2023

+   Created discord bot handling
+   Fixed duplication of notifications
+   Added help|watch|unwatch commands

```