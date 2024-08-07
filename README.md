# **TwitchDiscordNotifications**
![Static Badge](https://img.shields.io/badge/Version-v3.0-8ebff1?style=for-the-badge&logo=v)
![Static Badge](https://img.shields.io/badge/Language-python-3776ab?style=for-the-badge&logo=python)
![Static Badge](https://img.shields.io/badge/License-GNU%20GPL%20v3-blue.svg?style=for-the-badge)  

Get notifications of your favorite streamers on your discord Dm's


## Setting up the bot as a user  !!No longer up host your own bot!!
If you simply wish to use the bot without any setup or hosting necessary simply Join my server and ping the bot either on bot's dm's or on the discord server, he will reply with the prefix. Use the command Help to know what you can do.  
[Join TwitchStreamChecker Server](https://discord.gg/gbdPCxNavc) 
#### **OR**  
[Invite TwitchStreamChecker](https://discord.com/api/oauth2/authorize?client_id=1124891382595727460&permissions=8&scope=bot) 

## Setting up the bot as a host  
You will need to make an application on twitch and gets it's client id and client secret aswell as making it's Auth redirect link to **"https://twitchapps.com/tokengen/"**

## **Important links if you self host**
Twitch Client_id  and Client_secret(Application): https://dev.twitch.tv/console/apps  
### Bot now gets the Auth token automatically but if it fails use:   
**(OAuth redirect link must be "https://twitchapps.com/tokengen/")**  
Twitch OAuth key: https://twitchapps.com/tokengen/  
![OAuth](https://i.imgur.com/fuHBvHK.png)  
Discord bot: https://discord.com/developers/applications/


## Preview  
![notification preview](https://i.imgur.com/hpgxark.png)  
![notification preview](https://i.imgur.com/Dx6LxR6.png)


## **Usage**  
### **Commands**
#### **Works on Bots DMs or Any Channel on any Guild the Bot is a Member Of**  
**Help** - Shows list of commands.  
**Watch streamername or streamerlink** - Will get the user id and create a new list if it doesn't exist otherwise it will add the streamer to that users list.  
**Unwatch streamername or streamerlink** - Removes the streamer from that user's list.  
**Clear** - Deletes all the messages sent by the bot (1per second to avoid being rate limited).  
**List** - Generates a embed with all the watchlist streamers.  
**Configprefix** - Changes the prefix on that guild.  
**Configrole** - Changes the role given to every new member of guild.  
**Invite** - Generates bot invite link.  
**Ungerister** - Permanently deletes user's watchlist and data.  
**Stats** - Shows bots stats.  
**Restart** - Restarts the bot (available only to bot host).  
**Reload** - Reloads all the commands (available only to bot host)
**Stop** - Stops the bot (available only to bot host)
#### Replit
**It should create the secrets automatically so just change the filler text in there**

## Changes
```diff

### v3.0 11/12/2023

+   Fixed a bug that would crash bot when checking for updates


### v2.9 08/12/2023

+   Fixed bug with exit window on UI
+   Made send notification retry 3 times if it fails due to discord server issues (might be a litle unstable)
+   Organized some code
+   Bot now creates a backup of the database every hour with a limit of 12 files

### v2.8 26/11/2023

+   Fixed a bug with autoupdater that would crash the bot
+   Improved error handler
+   Added Stop bot command


### v2.7 31/10/2023

-   Removed image generation from List and Watch for optimization
+   Made commands case insensitive 
+   If Auth token expires bot will get a new one by itself
+   Fixed timestamp function
+   Added UI for bot config v1.0
+   Improved Performance decorator
+   Improved Stats command
+   Fixed some small bugs
+   Organized files
+   Fixed issues with required folders not being made
+   Added more information to the .env error
+   Improved on_error event
+   Fixed get_version and get_changelog
+   Improved Changelog embed

### v2.6 21/10/2023

+   Optimized code on main.py
+   Added CPU and Memory usage to stats command
+   Fixed some bugs with log_print
+   Modified intents error catcher

### v2.5 20/10/2023

!   Working on a UI
+   Fixed some minor issues
+   Added a cache system to reduce de number of requests
+   Added multiple streamer input on unwatch command

### v2.4 19/10/2023

+   Improved visual of changelog on update embed
+   Added changelog to the update embed
+   Added multiple streamer input on watch command
+   Improved Stats command filesize display
+   Improved command loader performance counter
+   Removed unecessary repetition of print(" " * console_width, end="\r")

### v2.3 17/10/2023

+   Fixed a major issue with autoupdater
+   Fixed a bug with auto updater
+   Fixed some small issues
+   Fixed a bug with keyboard interrupt handler
+   Fixed a small issue with command not found 

### v2.2 08/10/2023

+   Improved overall performance
+   Fixed streamers not leaving processed_streamers
+   Added custom decorator for debbugging
+   Added autoupdater
+   Added more information to stats command
+   Improved send_notification

### v2.1 07/10/2023

+   Increased SQLhandler performance
+   Fixed minor issues with commands
+   Implemented tests
+   Fixed send_notification bug
+   Improved help command
+   Better console UI
+   Added cooldown to clear command to prevent rate limit

### v2.1 06/10/2023

+   Restructured main.py code
+   Fixed List command bug
+   Added reload commands command
+   Fixed Bot not logging in when owner not in a guild with bot
+   Fixed small issues with clear command
+   Fixed error with mention for prefix
+   Moved from json to Sqlite for data

### v2.0 05/10/2023 Thanks to CDJuaum

!   Working on Slash Commands
!   Working on a better log system
!   Working on a more efficient and reliable way to save user watchlists 
+   Finished moving commands to individual files
+   Removed duplicated functions
+   Added change console title
+   Made commands loading faster
+   Added catch to Intents error
+   Made bot get owner.id by itself
+   Added timestamps to all embeds
+   Fixed small issue with watch command
+   Bot logs errors instead of sending in DMs
+   Added event listener to on guild remove
+   Completely reorganized the code into subsections in different files
+   Bot expansion easier 

### v1.9 04/10/2023

+   Moved Config Handler to it's own file
+   Made a better guild detector
+   Fixed some small issues

### v1.9 30/09/2023

+   Made log_print limit logged lines to 1k
+   Fixed a bug with log_print
+   Added Streamer names to top of pfp on list command

### v1.9 29/09/2023

+   Removed unecessary request on send_notification
+   Added custom keyboard interrupt handler
+   Added a function to allow bot restart without notification spam for already streaming streamers
+   Added a stats command
+   Added a restart bot command available to bot hosts
+   Added some missing embeds
+   Added a log system (early stages)

### v1.8 25/09/2023

+   Added username to console UI sucessfull notification message
+   Fixed small bug with send_notifications
+   Added unregister command
+   Made help command display commands in alphabetical order
+   Made some console UI changes
+   Fixed minor bug in check_stream

### v1.7 24/09/2023

+   Cleaner console UI
+   General optimization
+   Huge check_stream function speed increase
+   Huge list command speed increase
+   Fixed some small bugs

### v1.6 23/09/2023

+   Fixed some bugs with mention bot for prefix

### v1.6 22/09/2023

+   Made some config commands
+   Fixed some typos
+   Added multi-guild support
+   Added missing command descriptions
+   Fixed wrong time being shown on local timestamp

### v1.5 19/09/2023

+   Made the streamer checker faster
+   Made list image generation faster
+   Fixed some bugs

### v1.4 17/09/2023

+   Added invite me command
+   Fixed the local timezone being wrong on replit and for users with different timezone from script host
+   Optimized code and fixed some issues
+   Changed bot data handling from .ini to json
+   Changed the way the bot works to function with commands instead of plain messages
+   Complete rewrite of code

### v1.3 02/09/2023

!   Working on better config/data handler
+   Made list command show image of combined streamers profile pictures
+   Added amount of viewers in stream to notifications embed
+   Added stream game to notifications embed
+   Added stream title to notification embed

### v1.2 04/07/2023

+   Fixed streamers added after bot initialization not getting checked
+   Made console interface better, showing checking when checking streamer and showing currently streaming streamers
+   Cleaner console
+   Fixed if a streamer was removed from everybodys watchlist, it wouldn't leave the currently streaming list
+   Added stream started at, local  time to notification


### v1.1 03/07/2023

+   Added option to use watch with streamername or streamer link
+   Made the notification embeds prettier
+   Added clear command to delete all notifications sent by the bot

### v1.0 02/07/2023

+   Created discord bot handling
+   Fixed duplication of notifications
+   Added help|watch|unwatch commands

```
