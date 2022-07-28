import const
import config
import logging
from utils.email import send_email
from utils.storage import User, Image, Transaction
from utils.draw_qr_code_img import draw_qr_code_by_percentage
from utils.mint_nft import mint_nft

logging.basicConfig(filename=config.LOG_PATH, level=logging.INFO)


def failed_handler(event):
    charge_id = event["data"]["id"]

    # check if trans. exist by charge_id and get user_id
    transaction = Transaction.get(by='charge_id', value=charge_id)

    if transaction is None:
        logging.info(f"couldn't find transaction by charge_id, event info: {event}")
        return 'success', 200

    # get recipent's email by user id
    user = User.get(by='id', value=transaction.user_id)

    Transaction.update(charge_id=charge_id, column='status', value=const.FAILED_COINBASE_STATUS)

    send_email(config.EMAIL_USER,
               config.EMAIL_PASSWORD,
               user.email,
               config.EMAIL_SUBJECT,
               config.EMAIL_BODY_FAILED,
               config.IMAGES_FOLDER,
               []
               )

    logging.info(f"charge failed, event info: {event}")


def pending_handler(event):
    charge_id = event["data"]["id"]
    blockchain_trans_id = event["data"]["payments"][0]["transaction_id"]

    # check if trans. exist by charge_id
    transaction = Transaction.get(by='charge_id', value=charge_id)

    if transaction is None:
        logging.info(f"coundn't find transaction by charge_id, event info: {event}")
        return 'success', 200

    # update trans status to pending and set blockchain_trans_id
    Transaction.update(charge_id=charge_id, column='status', value=const.PENDING_COINBASE_STATUS)
    Transaction.update(charge_id=charge_id, column='blockchain_trans_id', value=blockchain_trans_id)

    logging.info(f"charge pending, event info: {event}")


def confirmed_handler(event):
    files = []
    charge_id = event["data"]["id"]
    blockchain_trans_id = event["data"]["payments"][0]["transaction_id"]

    # check if trans. exist by charge_id and get user_id
    transaction = Transaction.get(by='charge_id', value=charge_id)

    if transaction is None:
        logging.info(f"couldn't find transaction by charge_id, event info: {event}")
        return 'success', 200

    if event.type == const.CONFIRMED_CHARGE_EVENT:
        return 'success', 200

    print(event.type)

    # get recipent's email by user id
    user = User.get(by='id', value=transaction.user_id)

    # get images
    images = Image.get(limit=transaction.count_images_requested, is_sent=False)

    if images is None:
        logging.info(f"couldn't get images")
        return 'success', 200

    for image in images:
        files.append(image.file_name)
        Image.update(image.id, 'is_sent', True)

    # update trans status to confirmed and set images_id_arr and blockchain_trans_id
    Transaction.update(charge_id=charge_id, column='status', value=const.CONFIRMED_COINBASE_STATUS)
    Transaction.update(charge_id=charge_id, column='images_id_arr', value=str(files))
    Transaction.update(charge_id=charge_id, column='blockchain_trans_id', value=blockchain_trans_id)

    # get user percentage
    total_images_count = Transaction.sum_images(user_id=user.id)

    if total_images_count is None:
        logging.info(f"couldn't find transaction by user id, event info: {event}")
        return 'success', 200

    percentage = total_images_count * 100 / config.TOTAL_IMAGES_COUNT

    # send email with files
    send_email(config.EMAIL_USER,
               config.EMAIL_PASSWORD,
               user.email,
               config.EMAIL_SUBJECT,
               config.EMAIL_BODY_SUCCESS % (percentage, config.DOMAIN),
               config.IMAGES_FOLDER,
               files
               )

    logging.info(f"charge confirmed, event info: {event}")

    # redraw qr code img for web
    confirmed_images_count = Transaction.sum_images()

    if confirmed_images_count is None:
        confirmed_images_count = 0

    percentage = confirmed_images_count * 100 / config.TOTAL_IMAGES_COUNT

    logging.info(f"Starting rendering...")
    draw_qr_code_by_percentage(percentage)
    logging.info(f"Successful rendering")

    logging.info(f"Starting minting...")
    mint_nft(user.addr)
    logging.info(f"Successful minting")
