from email import message
from email.mime.text import MIMEText
import smtplib

def sendEmail(emailAddress, height, averageHeight, count):
    fromEmail = "testcsemail1@gmail.com"
    fromPassword = "testemail"
    toEmail = emailAddress

    subject = "Data"
    msg = "hello <strong>{0}</strong>. Average heights of {1} people are {2}".format(height, count, averageHeight)

    msg = MIMEText(msg, "html")
    msg["Subject"] = subject
    msg["To"] = toEmail
    msg["From"] = fromEmail
    msg["name"]

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(fromEmail, fromPassword)
    gmail.send_message(msg)




