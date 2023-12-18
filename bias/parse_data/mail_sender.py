import os
import json
import smtplib, ssl
from email.mime.text import MIMEText

import pandas as pd
from tqdm import tqdm

_SUBJECT = "Zugangsdaten JupyterHub | Data Science Foundations"


def _check_input(file_path: str, secrets: dict) -> bool:
    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return False

    if secrets is None:
        print("Please fill out the secrets.json file.")
        return False

    if (
        secrets["Mail"] is None
        or secrets["Mail"] == ""
        or secrets["Password"] is None
        or secrets["Password"] == ""
        or secrets["smtp-server"] is None
        or secrets["smtp-server"] == ""
        or secrets["port"] is None
        or secrets["port"] == 0
    ):
        print(
            "Please fill out the secrets.json file. It is missing the mail or password field. It should look like this: \n"
        )
        print(
            """
{
    "Mail": "",
    "Password": "",
    "smtp-server": "smtp.uni-hannover.de",
    "port": 587
}
"""
        )
        return False

    return True


def _generate_mail_text(mail: str, passwd: str, user: str) -> str:
    body = f"""
Guten Tag,

anbei erhalten Sie Ihren persönlichen Account, um JupyterHub auf dem 
LUIS-Cluster zu nutzen und 
dort die Übungen und semesterbegleitenden Assignments zu bearbeiten und 
einzureichen. 
Bitte beachten Sie, dass Sie sich entweder im Studiennetz befinden oder mittels VPN 
verbinden müssen, um auf die LUIS-Cluster zugreifen zu können.

Für Rückfragen bzgl. des Accounts richten Sie sich bitte an {mail}. 

Benutzername:   {user}
Passwort:       {passwd}

Mit freundlichen Grüßen,

Tim Ruhkopf, M.Sc. 
Institut für Künstliche Intelligenz 
Leibniz Universität Hannover 
Appelstr. 9A, 30167 Hannover, Germany 
"""

    return body


def send_mails(file_path: str, secrets: dict):
    if not _check_input(file_path, secrets):
        return

    sender_mail = secrets["Mail"]
    passwd = secrets["Password"]
    smtp_addr = secrets["smtp-server"]
    port = secrets["port"]

    df = pd.read_csv(file_path)

    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_addr, port)
    server.starttls(context=context)
    server.login(sender_mail, passwd)

    pbar = tqdm(df.iterrows(), total=len(df))
    for _, row in pbar:
        pbar.set_description(f"Sending mail to {row['E-Mail']}")

        msg = MIMEText(
            _generate_mail_text(sender_mail, row["Passwort"], row["Nutzernamen"])
        )
        msg["Subject"] = _SUBJECT
        msg["From"] = sender_mail
        msg["To"] = row["E-Mail"]

        server.sendmail(sender_mail, row["E-Mail"], msg.as_string())
    server.quit()


if __name__ == "__main__":
    with open("secrets.json", "r") as config_file:
        config = json.load(config_file)

    send_mails("../tests/testMails.csv", config)
