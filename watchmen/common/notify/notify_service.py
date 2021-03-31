from notifiers import get_notifier

from watchmen.common.alarm import AlarmMessage
from watchmen.config.config import settings


async def send_notifier(message: AlarmMessage):
    provider = get_notifier(settings.NOTIFIER_PROVIDER)
    if settings.EMAILS_ENABLED:
        # provider.defaults["from"]="andyxf1029@gmail.com"
        provider.notify(to=settings.EMAILS_TO, subject="this is alarm mail from watchmen data platform",
                        message="[" + message.severity + "] :" + message.message, from_=settings.EMAILS_FROM_EMAIL,
                        username=settings.SMTP_USER, password=settings.SMTP_PASSWORD, host=settings.SMTP_HOST,
                        port=settings.SMTP_PORT, tls=settings.SMTP_TLS)
