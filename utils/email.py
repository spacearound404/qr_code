import base64
import smtplib
import logging
import traceback
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


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
                with open(file_path + file, 'rb') as f:
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
    except Exception as e:
        logging.info(f"something went wrong while sending email to {mail_to} with files: {str(files)}")
        logging.info(str(e))
        logging.info(str(traceback.format_exc()))
