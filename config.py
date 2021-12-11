# coinbase config
API_KEY = ""
WEBHOOK_SECRET = ""

# database config
NAME_DB = ""
CLEAR_DB = False

# images config
IMAGES_FOLDER = ""

# logs config
CLEAR_LOGS = False

# ngrok config
NGROK_DOMAIN = ""

# email config
EMAIL_USER = ""
EMAIL_PASSWORD = ""
EMAIL_SUBJECT = "QR Code Event"
EMAIL_BODY_SUCCESS = f'''
'''

EMAIL_BODY_FAILED = f'''
<html>
    <head>
        <meta http-equiv=Content-Type content="text/html; charset=windows-1251">
        <meta name=Generator content="Microsoft Word 15 (filtered)">
    </head>
    <body lang=RU>
        <div class=WordSection1>
            <p class=MsoNormal><span lang=EN-US>Something went wrong at the time of payment</span></p>
            <p class=MsoNormal>&nbsp;</p>
            <a href="{NGROK_DOMAIN}">Try again</a>
            <p class=MsoNormal>&nbsp;</p>
            <p class=MsoNormal>© QR Code 2021</p>
        </div>
    </body>
</html>
'''
