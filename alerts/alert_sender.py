import smtplib
import ssl
import traceback
import config
import logger
import gnupg
from email.mime.text import MIMEText


class EmailSender:

    def __init__(self):
        self.host = config.get_smtp_server_host()
        self.port = config.get_smtp_server_port()
        self.user = config.get_smtp_user()
        self.password = config.get_smtp_password()
        self.sender = config.get_smtp_sender()
        self.receiver = config.get_smtp_receiver()
        self.smtp_client = None

    def send(self, email_body, subject='IVA Alert'):
        email = self.create_email(subject, email_body)
        return self.send_email(email)

    def create_email(self, subject, body):
        msg = create_mime_obj(body)
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = self.receiver
        return msg

    def send_email(self, email):
        logger.info('SMTP - trying to send email')
        try:
            self.create_smtp_client()
            self.smtp_login()
            self.smtp_send(email)
            self.smtp_client.quit()
            logger.info('SMTP - email successfully sent')
            return True
        except Exception:
            logger.error('SMTP - unable to send email')
            logger.error('SMTP - ' + str(traceback.format_exc()))
            return False

    def create_smtp_client(self):
        if config.is_smtps_enabled():
            self.smtp_client = smtplib.SMTP_SSL(self.host, self.port, context=create_ssl_context())
        else:
            self.smtp_client = smtplib.SMTP(self.host, self.port)
            self.starttls()

    def starttls(self):
        if config.is_smtp_starttls_enabled():
            try:
                self.smtp_client.ehlo()
                self.smtp_client.starttls(context=create_ssl_context())
            except smtplib.SMTPHeloError:
                logger.error('SMTP - The server did not reply properly to the HELO greeting')
            except smtplib.SMTPException:
                logger.error('SMTP - The server does not support the STARTTLS extension')
            except RuntimeError:
                logger.error('SMTP - SSL/TLS support is not available to your Python interpreter')

    def smtp_login(self):
        self.smtp_client.login(self.user, self.password)

    def smtp_send(self, email):
        self.smtp_client.sendmail(self.sender, [self.receiver], email.as_string())


def create_ssl_context():
    if config.is_verify_smtp_server_cert_enabled():
        return ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=config.get_smtp_ca_cert_file())
    return None


def create_mime_obj(body):
    if config.is_gpg_encryption_enabled():
        return MIMEText(encrypt_body(body))
    return MIMEText(body)


def encrypt_body(body):
    gnu = create_gpg_obj()
    import_keys(gnu)
    return encrypt(body, gnu)


def create_gpg_obj():
    return gnupg.GPG(homedir=config.get_gpg_home_dir())


def encrypt(body, gpg):
    return str(gpg.encrypt(body, get_pub_key_fingerprint(gpg)))


def import_keys(gnu):
    with open(config.get_gpg_pub_key_file(), 'r') as f:
        gnu.import_keys(f.read())


def get_pub_key_fingerprint(gnu):
    return gnu.list_keys()[0].get('fingerprint')
