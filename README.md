# @AbeliteBot on Telegram

##  Intro
Hello,
You can implement your own bot api and other information to do bookkeeping with this code.

I use Google Spreadsheet as the backend to record everything, and heroku as the webhook between Bot and Backend.

So there are some configurations you need to change.
1. bot api 
2. spreadsheet api (if you use google spreadsheet) / or your own backend


## Bot usage

1. Setup api key on BotFather and save into "token.txt"
2. Also you can preset validated user's id and its script url under the token.txt 

```
;token.txt
[CONFIG]
TOKEN = $YOUR_TOKEN

[USER]
$telegram_user_id = "$telegram_user_api_url"
```


## GoogleScript usage
1. upload googlaAppScript.gs to you Google App Scripts.
2. Get your spreadsheet id and replace it on line 6.
3. Make sure you do deploy as a web app.


## There are more functions to be added in next version.
1. ill figure it out what to add.
