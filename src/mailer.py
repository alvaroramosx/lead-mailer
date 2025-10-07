import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


def build_mail(
    from_addr: str,
    to_addr: str,
    subject: str,
    body: str,
    reply_to: Optional[str] = None,
    is_html: bool = False,
) -> MIMEMultipart:
    """Construye un mensaje MIME con asunto y cuerpo (texto o HTML)."""

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    part = MIMEText(body, "html" if is_html else "plain", _charset="utf-8")
    msg.attach(part)
    return msg


def send_email(
    host: str,
    port: int,
    username: Optional[str],
    password: Optional[str],
    use_ssl: bool,
    message: MIMEMultipart,
) -> None:
    """Envía un mensaje usando SMTP con SSL o STARTTLS si está disponible."""

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=host, port=port, context=context) as server:
            if username and password:
                server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host=host, port=port) as server:
            server.ehlo()
            try:
                server.starttls(context=ssl.create_default_context())
            except smtplib.SMTPException:
                # STARTTLS no disponible; continua sin TLS
                pass
            if username and password:
                server.login(username, password)
            server.send_message(message)


