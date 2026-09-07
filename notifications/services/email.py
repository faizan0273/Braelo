'''Central email send + template rendering. Views must not call SMTP directly.'''

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger('notifications.email')

SAFE_DELIVERY_MESSAGE = (
    'Unable to send email right now. Please try again later.'
)


class EmailDeliveryError(Exception):
    """SMTP/email failure with a client-safe message (never leak SMTP internals)."""

    def __init__(self, message: str = SAFE_DELIVERY_MESSAGE):
        super().__init__(message)


BRAND_NAME = 'Braelo'
BRAND_COLOR = '#CD9403'


@dataclass(frozen=True)
class EmailTemplate:
    key: str
    subject: str
    html: str
    text: str


class EmailTemplateService:
    TEMPLATES = {
        'verify_email': EmailTemplate(
            key='verify_email',
            subject='Verify your Braelo email',
            html='email/verify_email.html',
            text='email/verify_email.txt',
        ),
        'welcome': EmailTemplate(
            key='welcome',
            subject='Welcome to Braelo',
            html='email/welcome.html',
            text='email/welcome.txt',
        ),
        'password_reset': EmailTemplate(
            key='password_reset',
            subject='Your Braelo password reset code',
            html='email/password_reset.html',
            text='email/password_reset.txt',
        ),
        'password_changed': EmailTemplate(
            key='password_changed',
            subject='Your Braelo password was changed',
            html='email/password_changed.html',
            text='email/password_changed.txt',
        ),
        'security_alert': EmailTemplate(
            key='security_alert',
            subject='Security alert on your Braelo account',
            html='email/security_alert.html',
            text='email/security_alert.txt',
        ),
        'listing_created': EmailTemplate(
            key='listing_created',
            subject='Your Braelo listing is live',
            html='email/listing_created.html',
            text='email/listing_created.txt',
        ),
        'business_activated': EmailTemplate(
            key='business_activated',
            subject='Your Braelo business profile is ready',
            html='email/business_activated.html',
            text='email/business_activated.txt',
        ),
        'support_reply': EmailTemplate(
            key='support_reply',
            subject='Support replied to your Braelo request',
            html='email/support_reply.html',
            text='email/support_reply.txt',
        ),
    }

    def get(self, template_key: str) -> EmailTemplate:
        template = self.TEMPLATES.get(template_key)
        if template is None:
            raise ValueError(f'Unknown email template: {template_key}')
        return template

    def render(self, template_key: str, context: dict | None = None):
        template = self.get(template_key)
        payload = {
            'brand_name': BRAND_NAME,
            'brand_color': BRAND_COLOR,
            'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
            **(context or {}),
        }
        html = render_to_string(template.html, payload)
        text = render_to_string(template.text, payload)
        subject = payload.get('subject') or template.subject
        return subject, html, text


class EmailService:
    def __init__(self, templates: EmailTemplateService | None = None):
        self.templates = templates or EmailTemplateService()

    def send(
        self,
        *,
        to,
        template_key: str,
        context: dict | None = None,
        fail_silently: bool = False,
    ) -> bool:
        recipients = [addr for addr in _as_recipients(to) if addr]
        if not recipients:
            if fail_silently:
                return False
            raise ValueError('Email recipient is required.')

        subject, html, text = self.templates.render(template_key, context)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None
        if not _email_backend_ready():
            logger.error(
                'Email backend missing; cannot send template=%s to=%s',
                template_key,
                recipients,
            )
            if fail_silently:
                return False
            raise EmailDeliveryError()
        try:
            if _acs_backend_ready():
                try:
                    _send_via_acs(
                        subject=subject,
                        html=html,
                        text=text,
                        recipients=recipients,
                        from_email=from_email,
                    )
                    return True
                except Exception as acs_exc:
                    logger.warning(
                        'ACS send failed (%s); falling back if another backend is ready',
                        type(acs_exc).__name__,
                    )
                    if not _smtp_backend_ready():
                        raise EmailDeliveryError() from acs_exc
            message = EmailMultiAlternatives(
                subject=subject,
                body=text,
                from_email=from_email,
                to=recipients,
            )
            message.attach_alternative(html, 'text/html')
            message.send(fail_silently=False)
            return True
        except (smtplib.SMTPException, OSError, EmailDeliveryError) as exc:
            logger.exception(
                'Failed to send email template=%s to=%s',
                template_key,
                recipients,
            )
            if fail_silently:
                return False
            if isinstance(exc, EmailDeliveryError):
                raise
            raise EmailDeliveryError() from exc
        except Exception:
            logger.exception(
                'Failed to send email template=%s to=%s',
                template_key,
                recipients,
            )
            if fail_silently:
                return False
            raise EmailDeliveryError()

    def send_best_effort(self, *, to, template_key: str, context: dict | None = None) -> bool:
        return self.send(
            to=to,
            template_key=template_key,
            context=context,
            fail_silently=True,
        )


def _acs_backend_ready() -> bool:
    connection = (getattr(settings, 'AZURE_COMMUNICATION_CONNECTION_STRING', '') or '').strip()
    sender = (getattr(settings, 'ACS_EMAIL_SENDER', '') or '').strip()
    return bool(connection and sender)


def _smtp_backend_ready() -> bool:
    backend = (getattr(settings, 'EMAIL_BACKEND', '') or '').lower()
    if any(token in backend for token in ('locmem', 'console', 'dummy', 'inmemory')):
        return True
    user = (getattr(settings, 'EMAIL_HOST_USER', '') or '').strip()
    password = (getattr(settings, 'EMAIL_HOST_PASSWORD', '') or '').strip()
    return bool(user and password)


def _email_backend_ready() -> bool:
    return _acs_backend_ready() or _smtp_backend_ready()


def _acs_error_is_suppressed(exc: Exception) -> bool:
    blob = f'{type(exc).__name__} {exc}'.lower()
    return 'suppressed' in blob


def _delivery_aliases(address: str) -> list[str]:
    """
    Prefer a plus-alias for Gmail.

    Azure managed-domain mail often hard-bounces, then ACS suppresses the
    exact recipient. `user+tag@gmail.com` still delivers to `user@gmail.com`
    but is a different ACS recipient, so the OTP can go out.
    """
    import secrets
    from datetime import date

    addr = (address or '').strip()
    aliases: list[str] = []

    def _add(item: str) -> None:
        if item and item not in aliases:
            aliases.append(item)

    if '@' not in addr:
        _add(addr)
        return aliases
    local, domain = addr.split('@', 1)
    domain_l = domain.lower()
    local_base = local.split('+', 1)[0]
    if domain_l in ('gmail.com', 'googlemail.com'):
        _add(f'{local_base}+braelo@{domain_l}')
        _add(f'{local_base}+b{date.today().strftime("%m%d")}@{domain_l}')
        _add(f'{local_base}+b{secrets.token_hex(2)}@{domain_l}')
    _add(addr)
    return aliases


def _send_via_acs(*, subject: str, html: str, text: str, recipients: list[str], from_email: str | None) -> None:
    try:
        from azure.communication.email import EmailClient
    except Exception as exc:  # pragma: no cover - import environment
        logger.warning('azure-communication-email unavailable: %s', exc)
        raise EmailDeliveryError() from exc

    sender = (
        (getattr(settings, 'ACS_EMAIL_SENDER', '') or '').strip()
        or (from_email or '').strip()
    )
    if not sender:
        raise EmailDeliveryError()

    client = EmailClient.from_connection_string(
        getattr(settings, 'AZURE_COMMUNICATION_CONNECTION_STRING')
    )
    attempts = (
        _delivery_aliases(recipients[0])
        if len(recipients) == 1
        else [recipients]
    )
    last_exc: Exception | None = None
    for attempt in attempts:
        dest = attempt if isinstance(attempt, list) else [attempt]
        message = {
            'senderAddress': sender,
            'content': {
                'subject': subject,
                'plainText': text,
                'html': html,
            },
            'recipients': {
                'to': [{'address': addr} for addr in dest],
            },
        }
        try:
            client.begin_send(message).result()
            return
        except Exception as exc:
            last_exc = exc
            if not _acs_error_is_suppressed(exc):
                raise
            logger.warning(
                'ACS suppressed recipient=%s; retrying with a mailbox alias',
                dest,
            )
    if last_exc is not None:
        raise last_exc
    raise EmailDeliveryError()


def _as_recipients(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


email_service = EmailService()
email_templates = EmailTemplateService()
