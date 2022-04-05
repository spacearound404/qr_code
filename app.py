import os
import random
import config
import logging
from coinbase_commerce.client import Client
from coinbase_commerce.webhook import Webhook
from flask import Flask, render_template, request, jsonify
from coinbase_commerce.error import WebhookInvalidPayload, SignatureVerificationError

import const
import errors
from utils.storage import StorageORM, User, Image, Transaction
from webhook_handlers import failed_handler, pending_handler, confirmed_handler

# define web server (Flask)
app = Flask(__name__)
FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = FOLDER

# define logging
logging.basicConfig(filename=config.LOG_PATH, level=logging.INFO)

# define db (orm)
storage = StorageORM()
User.set_session(storage.session)
Image.set_session(storage.session)
Transaction.set_session(storage.session)


@app.route("/")
def index(domain_charge=None, domain_check=None, img_path=None, polygon_logo_path=None):
    screenshot = 'qr_code.jpg'
    polygon_logo = 'polygon_logo.png'
    charge_endpoint = '/charge'
    check_endpoint = '/check'

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], f'{screenshot}')
    full_polygonlogo = os.path.join(app.config['UPLOAD_FOLDER'], f'{polygon_logo}')

    return render_template('index.html',
                           domain_charge=f"{config.DOMAIN}{charge_endpoint}",
                           domain_check=f"{config.DOMAIN}{check_endpoint}",
                           img_path=full_filename,
                           polygon_logo_path=full_polygonlogo)


@app.route("/charge/success")
def success(domain=None):
    return render_template('success.html', domain=config.DOMAIN)


@app.route("/charge/cancel")
def cancel(domain=None):
    return render_template('cancel.html', domain=config.DOMAIN)


# charge images
@app.route("/charge", methods=['POST'])
def checkout():
    email = request.form['email']
    address = request.form['address']
    count_images_requested = int(request.form['count'])

    # price in USD
    total_amount = config.DEFAULT_ITEM_PRICE * count_images_requested

    # get valid count of images
    count_images_available = Image.count(is_sent=False)

    # validate count
    if count_images_requested == 0:
        return jsonify(error=errors.ERR_ZERO_IMAGE)
    elif count_images_available < count_images_requested:
        return jsonify(error=errors.ERR_IMAGE_COUNT, last_count=count_images_available)

    client = Client(api_key=config.API_KEY)

    charge_info = {
        "name": f"Part of QR-code | x{count_images_requested}",
        "description": f"Image which is part of the qr code, number of {count_images_requested}",
        "local_price": {
            "amount": str(total_amount),
            "currency": config.DEFAULT_CURRENCY
        },
        "pricing_type": config.PRICING_TYPE,
        "redirect_url": f"{config.DOMAIN}{config.CHARGE_SUCCESS_ENDPOINT}",
        "cancel_url": f"{config.DOMAIN}{config.CHARGE_CANCEL_ENDPOINT}"
    }

    charge = client.charge.create(**charge_info)

    logging.info(f"create charge, charge info: {charge_info}")

    charge_hosted_url = charge["hosted_url"]
    charge_id = charge["id"]
    charge_code = charge["code"]

    logging.info(f"charge_hosted_url: {charge_hosted_url}, \
                   charge_id: {charge_id}, \
                   charge_code: {charge_code}, \
                   email: {email}, \
                   count_images_requested: {count_images_requested}, \
                   item_price: {config.DEFAULT_ITEM_PRICE}, \
                   currency: {config.DEFAULT_CURRENCY}, \
                   total_amount: {total_amount}")

    User.add(addr=address, email=email)
    user = User.get(by='email', value=email)

    logging.info(f"add new user to db")

    Transaction.add(
        charge_hosted_url=charge_hosted_url,
        charge_id=charge_id,
        charge_code=charge_code,
        count_images_requested=count_images_requested,
        item_price=config.DEFAULT_ITEM_PRICE,
        total_amount=total_amount,
        status=const.NEW_COINBASE_STATUS,
        user_id=user.id
    )

    return jsonify(result=charge_hosted_url)


# check email's percentage
@app.route('/check', methods=['POST'])
def check():
    logging.info('hello')
    logging.info(dir(request.form))
    email = request.form['email']
    address = request.form['address']

    user = User.get(by='email', value=email)
    user = user if user else User.get(by='addr', value=address)

    if user is None:
        return jsonify(result=const.RESPONSE_USER_DOESNT_EXIST)

    total_images_count = Transaction.sum_images(user_id=user.id)

    percentage = total_images_count * 100 / config.TOTAL_IMAGES_COUNT

    return jsonify(result=percentage)


# get events from coinbase
@app.route('/webhooks', methods=['POST'])
def webhooks():
    request_data = request.data.decode('utf-8')
    request_sig = request.headers.get('X-CC-Webhook-Signature', None)
    event_func_dict = {
        const.FAILED_CHARGE_EVENT: failed_handler,
        const.PENDING_CHARGE_EVENT: pending_handler,
        const.CONFIRMED_CHARGE_EVENT: confirmed_handler
    }

    try:
        event = Webhook.construct_event(request_data, request_sig, config.WEBHOOK_SECRET)
        logging.info(f"charge event, event info: {event}")
    except (WebhookInvalidPayload, SignatureVerificationError) as e:
        logging.info(f"raised WebhookInvalidPayload or SignatureVerificationError error: {str(e)}")
        return str(e), 400

    event_func_dict[event.type](event)

    return 'success', 200


if __name__ == "__main__":
    app.run(debug=True, host=config.HOST, port=config.PORT)
