# coinbase config
API_KEY = '98f79ed7-6a39-4b1f-bf0f-d4fec9d81893'
WEBHOOK_SECRET = 'a13521ed-aee2-4ac3-bbfb-8cc5511c57b4'

# database config
NAME_DB = ''
CLEAR_DB = False

# images config
IMAGES_FOLDER = '/opt/qr_code/smartcontracts/images_test'

# logs config
CLEAR_LOGS = False

# host
HOST = '0.0.0.0'
PORT = 8000

# domain config
DOMAIN = 'https://beb7-77-108-97-164.ngrok.io'

# email config
EMAIL_USER = 'malevichtwentyfirst@gmail.com'
EMAIL_PASSWORD = 'Ricardoflexer69'
EMAIL_SUBJECT = 'QR Code Event'
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
            <a href="{DOMAIN}">Try again</a>
            <p class=MsoNormal>&nbsp;</p>
            <p class=MsoNormal>© QR Code 2021</p>
        </div>
    </body>
</html>
'''

SQLITE_PATH = 'sqlite:///storages/qr_code.db?check_same_thread=False'

# display in web page
QRCODE_IMG_PATH = './static/img/qr_code.jpg'
QRCODE_IMG_PIXEL_COUNT = 10000
QRCODE_IMG_RESOLUTION = 100

LOG_PATH = './logs/qr_code_app.log'

CHARGE_SUCCESS_ENDPOINT = '/charge/success'
CHARGE_CANCEL_ENDPOINT = '/charge/cancel'

PRICING_TYPE = 'fixed_price'

# USD
DEFAULT_ITEM_PRICE = 1
DEFAULT_CURRENCY = 'USD'

TOTAL_IMAGES_COUNT = 10000

# email
EMAIL_BODY_SUCCESS = f'''
        <html>
            <head>
                <meta http-equiv=Content-Type content="text/html; charset=windows-1251">
                <meta name=Generator content="Microsoft Word 15 (filtered)">
            </head>
            <body lang=RU>
                <div class=WordSection1>
                    <p class=MsoNormal><span lang=EN-US>1.</span></p>
                    <p class=MsoNormal><span lang=EN-US>101100111001011110011, now you are in
                    Event.</span></p>
                    <p class=MsoNormal><span lang=EN-US>Moreover,you are now part of my vision.</span></p>
                    <p class=MsoNormal><span lang=EN-US>Let's see the full idea.</span></p>
                    <p class=MsoNormal><span lang=EN-US>With all due respect, 1000100 1001011</span></p>
                    <p class=MsoNormal><span lang=EN-US>0404.</span></p>
                    <p class=MsoNormal><span lang=EN-US>&nbsp;</span></p>
                    <p class=MsoNormal><span lang=EN-US>2.</span></p>
                    <p class=MsoNormal><span lang=EN-US>Now you own %s of the
                    digital age art object.</span></p>
                    <p class=MsoNormal><span lang=EN-US>Soon you'll receive an NFT as your own
                    relict chunk.</span></p>
                    <p class=MsoNormal><span lang=EN-US>So let's see the full idea.</span></p>
                    <p class=MsoNormal>With all due respect  1000100 1001011.</p>
                    <p class=MsoNormal>0404.</p>
                    <p class=MsoNormal>&nbsp;</p>
                    <a href="%s">Buy more</a>
                    <p class=MsoNormal>&nbsp;</p>
                    <p class=MsoNormal>© QR Code 2022</p>
                </div>
            </body>
        </html>
        '''