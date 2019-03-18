# Code Search Bot 

I am a code search bot - I will help you find code snippets in your GitHub repo! Have you had the feeling that sometimes you are looking for a solution to the coding problem that you have solved before? 

I wanted to automate otherwise manual process of searching through GitHub repos and coding projects by building a bot that would do it all for me. 

After sending a message to the bot, it will skim through the pre-defined GitHub repository and return relevant coding snippets. 
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites & Installing

1. The bot is built in Python 3.6. I recommend to create a virtual environment with the following packages to get the bot running in your machine:
```
logging
telegram
linkGrabber
schedule
```

2. In addition to the above, you would need to create a bot in Telegram and assign the token of your bot in the environment file. 
More information about Telegram bots can be found here: https://core.telegram.org/bots

## Deployment

I have deployed the bot on Heroku, however you can use any other alternative that you are familar with. 

To deploy a bot on Heroku, follow the following steps:
```
1. Create the Heroku account and install the Heroku Toolbelt.
2. Login to your Heroku account using heroku login.
3. Go to the app's folder using cd ~/heroku-node-telegram-bot
4. Run heroku create to prepare the Heroku environment.
5. Run heroku config:set TOKEN=SET HERE THE TOKEN YOU'VE GOT FROM THE BOTFATHER and heroku config:set HEROKU_URL=$(heroku info -s | grep web_url | cut -d= -f2) to configure environment variables on the server.
6. Run git add -A && git commit -m "Ready to run on heroku" && git push heroku master to deploy your bot to the Heroku server.
```
Send smth to the bot to check out if it works ok.


## Authors

* [Nurbol Sakenov](https://github.com/nurcity)


## Acknowledgments

* [heroku-node-telegram-bot](https://github.com/odditive/heroku-node-telegram-bot)
* [How to Create and Deploy a Telegram Bot using Python?](https://github.com/odditive/heroku-node-telegram-bot)
* [Telegram bot examples](https://github.com/odditive/heroku-node-telegram-bot)
