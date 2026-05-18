import ssl
import certifi
import os

from dotenv import load_dotenv

from sendgrid import (
    SendGridAPIClient
)

from sendgrid.helpers.mail import (
    Mail
)

load_dotenv()


def send_reset_email(
    email,
    token
):

    try:

        reset_link = (
            f"http://localhost:5173/reset-password/{token}"
        )

        message = Mail(

            from_email=
            "chiranjeevitellagorla2004@gmail.com",

            to_emails=
            email,

            subject=
            "burst",

            html_content=f"""

            <h2>
            Reset Password
            </h2>

            <p>
            Click below:
            </p>

            <a href="{reset_link}">
            Reset Password
            </a>

            """
        )

        ssl._create_default_https_context = (

            lambda:

            ssl.create_default_context(
                cafile=
                certifi.where()
            )
        )

        sg = SendGridAPIClient(

            os.getenv(
                "SENDGRID_API_KEY"
            )
        )

        response = sg.send(
            message
        )

        print(
            "MAIL SENT:",
            response.status_code
        )

    except Exception as e:

        print(
            "MAIL ERROR:",
            e
        )