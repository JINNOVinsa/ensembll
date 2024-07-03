import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

class Mailling:
    
    def __init__(self, host, pswd, port=587, smtp_server="smtp.gmail.com"):
        self.smtp_server = smtp_server
        self.host = host
        self.pswd = pswd
        self.port = port

        self.server = None

    def connect(self):
        try:
            print("Start connect")
            context = ssl.create_default_context()
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            print("Server created")
            self.server.ehlo()
            self.server.starttls(context=context)
            print("TLS engaged")
            self.server.ehlo()
            self.server.login(self.host, self.pswd)
            print("Connected")
        except Exception as e:
            print(e)

    def disconnect(self):
        if self.server is not None:
            self.server.quit()

    def buildmail(self, receiver, subject, content, image_path=None):
        message = MIMEMultipart("related")
        message["From"] = self.host
        message["To"] = receiver
        message["Subject"] = subject

        message_alt = MIMEMultipart("alternative")
        message.attach(message_alt)

        message_alt.attach(MIMEText(content, "html"))

        if image_path:
            with open(image_path, 'rb') as img_file:
                msg_img = MIMEImage(img_file.read(), name=os.path.basename(image_path))
                msg_img.add_header('Content-ID', '<park7_logo>')
                message.attach(msg_img)

        return message
    
    def sendmail(self, dest, content):
        self.server.sendmail(self.host, dest, content.as_string())