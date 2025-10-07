import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Optional


def build_mail(
    from_addr: str,
    to_addr: str,
    subject: str,
    body: str,
    reply_to: Optional[str] = None,
    is_html: bool = False,
    inline_logo_path: Optional[str] = None,
    inline_logo_cid: str = "logo",
) -> MIMEMultipart:
    """Construye un mensaje MIME; soporta imagen inline vía CID cuando es HTML.

    Cuando `inline_logo_path` está definido y `is_html` es True, adjunta la imagen
    y puede referenciarse en el HTML como `cid:logo` (o el CID indicado).
    """

    if is_html and inline_logo_path:
        msg = MIMEMultipart("related")
        alt = MIMEMultipart("alternative")
        msg.attach(alt)
        html_part = MIMEText(body, "html", _charset="utf-8")
        alt.attach(html_part)
        try:
            with open(inline_logo_path, "rb") as f:
                img = MIMEImage(f.read())
            img.add_header("Content-ID", f"<{inline_logo_cid}>")
            img.add_header("Content-Disposition", "inline")
            msg.attach(img)
        except Exception:
            # Si falla el logo, continuamos con solo el HTML
            pass
    else:
        msg = MIMEMultipart()
        part = MIMEText(body, "html" if is_html else "plain", _charset="utf-8")
        msg.attach(part)

    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
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


