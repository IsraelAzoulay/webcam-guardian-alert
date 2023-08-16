import smtplib
import imghdr
import os
from dotenv import load_dotenv
from email.message import EmailMessage

# Load environment variables from .env file
load_dotenv()
SENDER = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER = os.getenv("RECEIVER_EMAIL")


def send_email(image_path):
    # Creating an object fof the 'EmailMessage' class, and it behaves as a dictionary.
    email_message = EmailMessage()
    email_message["Subject"] = "New customer showed up!"
    # The body of the email.
    email_message.set_content("Hey, we just saw a new customer!")

    # Adding the attachment to the email, so we open the 'images' file in 'rb' mode (since it's a binary file) and
    # extract it's binary content.
    with open(image_path, "rb") as file:
        content = file.read()
    # Arguments explanation: 'maintype' - specifies what kind of file it is. 'subtype' - specifies what kind of
    # image type it is.
    email_message.add_attachment(content, maintype="image", subtype=imghdr.what(None, content))

    # Setting the gmail server, starting it and sending the email as a string. (It'll work only for gmail).
    # 'smtp.gmail.com' - is the host. '587' - is the port.
    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    # Starting the email server.
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())
    gmail.quit()


if __name__ == "__main__":
    send_email(image_path="images/19.png")

