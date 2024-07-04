import smtplib
import socket

from email.mime.text import MIMEText

import os
from dotenv import load_dotenv


class PostSend:
    def __init__(self, send_to: str):
        """
        All base email settings should be described in .env file.
        :param send_to: User email
        """

        dotenv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self.e_mail = os.getenv('e_mail')
        self.smtp = os.getenv('smtp')
        self.pwd = os.getenv('pwd')
        self.port = os.getenv('port')
        self.send_to = send_to

    def mail_send(self, subj: str, message: str):
        try:
            s = smtplib.SMTP_SSL(self.smtp, self.port)
        except socket.gaierror:
            return 'Connection error'

        print(f'self.e_mail: {self.e_mail}')

        if self.e_mail.split("@")[-1] in [
            'yandex.ru',
            'yandex.com',
            'yandex.by',
            'yandex.kz',
            'ya.ru'
        ]:
            login = self.e_mail.split("@")[0]
        else:
            login = self.e_mail

        s.login(login, self.pwd)

        mess = MIMEText(message, 'html')
        mess['From'] = self.e_mail
        mess['To'] = self.send_to
        mess['Subject'] = subj
        s.sendmail(self.e_mail, self.send_to, mess.as_string())
        s.quit()

        return f'The meaasage to {self.send_to} sended sucessefuly.'

    def __del__(self):
        self.mail_send(subj='Furnace. Work comp.',
                       message='End of the program.')
