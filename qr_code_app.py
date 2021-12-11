import os
import random
import config
import base64
import smtplib
import sqlite3
import logging
from email import encoders
from PIL import Image, ImageDraw
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from coinbase_commerce.client import Client
from coinbase_commerce.webhook import Webhook
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify
from coinbase_commerce.error import WebhookInvalidPayload, SignatureVerificationError


# define web server (Flask)
app = Flask(__name__)
FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = FOLDER


# define logging
logging.basicConfig(filename="logs/qr_code_app.log", level=logging.INFO)


# define database connection
conn = sqlite3.connect(config.NAME_DB, check_same_thread=False)
cursor = conn.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS 'users' (
	'id'	INTEGER,
	'email'	TEXT UNIQUE,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS 'images' (
	'id'	INTEGER,
	'file_name'	TEXT UNIQUE,
	'is_sent'	INTEGER,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS 'transactions' (
	'id'	INTEGER,
	'charge_hosted_url'	TEXT,
	'charge_id'	TEXT,
	'charge_code'	TEXT,
	'images_count'	INTEGER,
	'item_price'	INTEGER,
	'amount'	INTEGER,
	'status'	TEXT,
	'user_id'	INTEGER,
	'images_id_arr'	TEXT,
    'blockchain_trans_id' TEXT,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")


def send_email(mail_from, mail_pass, mail_to, mail_subject, mail_body, file_path, files):
    message = MIMEMultipart()
    message['From'] = mail_from
    message['To'] = mail_to
    message['Subject'] = mail_subject

    try:
        # configuring mail sending 
        message.attach(MIMEText(mail_body, 'html'))

        # if files len equal more then 0 then attach files
        if len(files) > 0:
            for file in files:
                with open(file_path+file, 'rb') as f:
                    payload = MIMEBase('application', 'octate-stream')
                    payload.set_payload((f).read())
                    encoders.encode_base64(payload) 
                    
                    payload.add_header('Content-Disposition', f'attachment; filename={file}')
                message.attach(payload)

        # setup smtp
        session = smtplib.SMTP('smtp.gmail.com', 587) 
        session.starttls() 
        session.login(mail_from, mail_pass) 
        msg = message.as_string()
        session.sendmail(mail_from, mail_to, msg)
        session.quit()

        logging.info(f"email was sent to {mail_to} successfully with files: {str(files)}")
    except:
        logging.info(f"something went wrong while sending email to {mail_to} with files: {str(files)}")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def draw_qr_code_by_percentage(percentage=0):
    arr = []
    max_count = 10000
    file_name = "./static/img/qr_code.jpg"
    black_pix_max_count = max_count * percentage / 100

    im = Image.new('RGB', (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    for i in range(max_count):
        if i <= black_pix_max_count:
            arr.append(1)
        else:
            arr.append(0)

    random.shuffle(arr)

    matrix = list(chunks(arr, 100))

    for y in range(100):
        for x in range(100):
            if matrix[x][y] == 0:
                draw.point(
                    xy=(
                        (x, y)
                    ), fill='white'
                )
            else:
                draw.point(
                    xy=(
                        (x, y)
                    ), fill='black'
                )

    os.remove(file_name)

    im.save(file_name, quality=100)


@app.route("/")
def index(ngrok_domain_charge=None, ngrok_domain_check=None, img_path=None):  
    screenshot = "qr_code.jpg"
    
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], f'{screenshot}')

    return render_template('index.html', ngrok_domain_charge=f"{config.NGROK_DOMAIN}/charge", ngrok_domain_check=f"{config.NGROK_DOMAIN}/check", img_path=full_filename)


@app.route("/charge/success")
def success(ngrok_domain=None):        
    return render_template('success.html', ngrok_domain=config.NGROK_DOMAIN)


@app.route("/charge/cancel")
def cancel(ngrok_domain=None):        
    return render_template('cancel.html', ngrok_domain=config.NGROK_DOMAIN)


# charge images
@app.route("/charge", methods=['POST'])
def checkout():        
    
    email = request.form['email']
    count = int(request.form['count'])

    # price in USD
    item_price = 1
    images_count_in_db = 0
    amount = item_price * count

    # get valid count for buy from db
    cursor.execute("SELECT count(id) FROM images WHERE is_sent = 0;")
    res = cursor.fetchone()

    if res is None:
        return jsonify(error="zero_image")

    images_count_in_db = res[0]

    # check count is valid for buy
    if images_count_in_db < count:
        return jsonify(error="image_count", last_count=images_count_in_db)

    client = Client(api_key=config.API_KEY)

    charge_info = {
        "name": f"Part of QR-code | x{count}",
        "description": f"Image which is part of the qr code, number of {count}",
        "local_price": {
            "amount": str(amount),
            "currency": "USD"
        },
        "pricing_type": "fixed_price",
        "redirect_url": f"{config.NGROK_DOMAIN}/charge/success",
        "cancel_url": f"{config.NGROK_DOMAIN}/charge/cancel"
    }

    charge = client.charge.create(**charge_info)
    
    logging.info(f"create charge, charge info: {charge_info}")

    chanrge_hosted_url = charge["hosted_url"]
    chanrge_id = charge["id"]
    charge_code = charge["code"]

    logging.info(f"chanrge_hosted_url: {chanrge_hosted_url}, chanrge_id: {chanrge_id}, charge_code: {charge_code}, email: {email}, count: {count}, item_price: {item_price}, amount: {amount}")

    cursor.execute("SELECT email FROM users WHERE email = ?;", (email,))
    res = cursor.fetchone()

    # if email isn't there then insert new row
    if res is None:
        cursor.execute("INSERT INTO users(email) VALUES(?);", (email,))
        conn.commit()

    # get user id by email
    cursor.execute("SELECT id FROM users WHERE email = ?;", (email,)) 
    res = cursor.fetchone()

    if res is None:
        return jsonify(result="user_id_doesnt_exist")

    user_id = res[0]
    status = "new"

    cursor.execute("INSERT INTO transactions(charge_hosted_url, charge_id, charge_code, images_count, item_price, amount, status, user_id, images_id_arr) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", (chanrge_hosted_url, chanrge_id, charge_code, count, item_price, amount, status, user_id, ""))
    conn.commit()

    logging.info(f"data saved in database successfully")

    return jsonify(result=chanrge_hosted_url)


# check email's percentage
@app.route('/check', methods=['POST'])
def check():
    email = request.form['email']
    cursor.execute("SELECT id FROM users WHERE email = ?;", (email,)) 
    res = cursor.fetchone()

    if res is None:
        return jsonify(result="user_doesnt_exist")

    user_id = res[0]

    cursor.execute("SELECT SUM(images_count) FROM transactions WHERE user_id = ? and status = 'confirmed' GROUP BY user_id;", (user_id,)) 
    res = cursor.fetchone()

    if res is None:
        return jsonify(result="user_doesnt_exist")

    images_count = int(res[0])
    percentage = images_count * 100 / 1000000

    return jsonify(result=percentage)


# get events from coinbase
@app.route('/webhooks', methods=['POST'])
def webhooks():
    request_data = request.data.decode('utf-8')
    request_sig = request.headers.get('X-CC-Webhook-Signature', None)

    try:
        event = Webhook.construct_event(request_data, request_sig, config.WEBHOOK_SECRET)
        logging.info(f"charge event, event info: {event}")
    except (WebhookInvalidPayload, SignatureVerificationError) as e:
        logging.info(f"raised WebhookInvalidPayload or SignatureVerificationError error: {str(e)}")
        return str(e), 400

    if event.type == "charge:failed":
        charge_id = event["data"]["id"]
        status = "failed"

        # check if trans. exist by charge_id and get user_id
        cursor.execute("SELECT * FROM transactions WHERE charge_id = ?;", (charge_id,)) 
        res = cursor.fetchone()

        user_id = int(res[8])

        # get recipent's email by user id
        cursor.execute("SELECT email FROM users WHERE id = ?;", (user_id,)) 
        res = cursor.fetchone()

        recipent_user_email = str(res[0])

        cursor.execute("UPDATE transactions SET status = ? WHERE charge_id = ?;", (status, charge_id,)) 
        conn.commit()

        send_email(config.EMAIL_USER, config.EMAIL_PASSWORD, recipent_user_email, config.EMAIL_SUBJECT, config.EMAIL_BODY_FAILED, config.IMAGES_FOLDER, [])

        logging.info(f"charge failed, event info: {event}")

    if event.type == "charge:pending":
        charge_id = event["data"]["id"]
        blockchain_trans_id = event["data"]["payments"][0]["transaction_id"]
        status = "pending"

        # check if trans. exist by charge_id
        cursor.execute("SELECT id FROM transactions WHERE charge_id = ?;", (charge_id,)) 
        res = cursor.fetchone()

        if res is None:
            logging.info(f"coundn't find transaction by charge_id, event info: {event}")
            return 'success', 200

        # update trans status to pending and set blockchain_trans_id
        cursor.execute("UPDATE transactions SET status = ?, blockchain_trans_id = ? WHERE charge_id = ?;", (status, blockchain_trans_id, charge_id,)) 
        conn.commit()

        logging.info(f"charge pending, event info: {event}")

    if event.type == "charge:confirmed":

        # get charge_id from response
        files = []
        images_count = 0
        status = "confirmed"
        charge_id = event["data"]["id"]
        blockchain_trans_id = event["data"]["payments"][0]["transaction_id"]

        # check if trans. exist by charge_id and get user_id
        cursor.execute("SELECT * FROM transactions WHERE charge_id = ?;", (charge_id,)) 
        res = cursor.fetchone()

        if res is None:
            logging.info(f"couldn't find transaction by charge_id, event info: {event}")
            return 'success', 200

        user_id = int(res[8])
        images_count = int(res[4])

        # get recipent's email by user id
        cursor.execute("SELECT email FROM users WHERE id = ?;", (user_id,)) 
        res = cursor.fetchone()

        recipent_user_email = str(res[0])

        # get file_name from images
        cursor.execute("SELECT * FROM images WHERE is_sent = 0 LIMIT ?;", (images_count,)) 
        res = cursor.fetchall()

        if res is None:
            logging.info(f"coundn't get file_name in images")
            return 'success', 200

        for img in res:
            file_id = img[0]
            file_name = img[1]

            files.append(file_name)

            # update is_sent in images by id
            cursor.execute("UPDATE images SET is_sent = 1 WHERE id = ?;", (file_id,)) 
            conn.commit()
        
        # update trans status to confirmed and set images_id_arr and blockchain_trans_id
        cursor.execute("UPDATE transactions SET status = ?, images_id_arr = ?, blockchain_trans_id = ? WHERE charge_id = ?;", (status, str(files), blockchain_trans_id, charge_id,)) 
        conn.commit()

        # get user percentage for email
        cursor.execute("SELECT SUM(images_count) FROM transactions WHERE user_id in (SELECT user_id FROM transactions WHERE blockchain_trans_id = ?);", (str(blockchain_trans_id),)) 
        res = cursor.fetchone()

        if res is None:
            logging.info(f"couldn't find transaction by blockchain_trans_id, event info: {event}")
            return 'success', 200

        images_count = int(res[0])
        percentage = images_count * 100 / 1000000

        # send email with files

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
                    <p class=MsoNormal><span lang=EN-US>Now you own more than {percentage}% of the
                    digital age art object.</span></p>
                    <p class=MsoNormal><span lang=EN-US>Soon you'll receive an NFT as your own
                    relict chunk.</span></p>
                    <p class=MsoNormal><span lang=EN-US>So let's see the full idea.</span></p>
                    <p class=MsoNormal>With all due respect  1000100 1001011.</p>
                    <p class=MsoNormal>0404.</p>
                    <p class=MsoNormal>&nbsp;</p>
                    <a href="{config.NGROK_DOMAIN}">Buy more</a>
                    <p class=MsoNormal>&nbsp;</p>
                    <p class=MsoNormal>© QR Code 2021</p>
                </div>
            </body>
        </html>
        '''

        send_email(config.EMAIL_USER, config.EMAIL_PASSWORD, recipent_user_email, config.EMAIL_SUBJECT, EMAIL_BODY_SUCCESS, config.IMAGES_FOLDER, files)
        logging.info(f"charge confirmed, event info: {event}")

        # redraw qr code img for web
        cursor.execute("SELECT SUM(images_count) FROM transactions WHERE status = 'confirmed';") 
        res = cursor.fetchone()

        percentage = 0

        if res is None:
            pass

        images_count = int(res[0])
        percentage = images_count * 100 / 1000000

        draw_qr_code_by_percentage(percentage)

    return 'success', 200


if __name__ == "__main__":
    app.run(debug=True)