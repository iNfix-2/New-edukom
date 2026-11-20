"""Explicit SMTP check: python test_smtp.py (never runs on import)."""
import os
import smtplib


def main():
    host = os.environ['EMAIL_HOST']
    port = int(os.environ.get('EMAIL_PORT', '587'))
    use_ssl = os.environ.get('EMAIL_USE_SSL', '').lower() == 'true'
    smtp = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with smtp(host, port, timeout=10) as server:
        if not use_ssl and os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true':
            server.starttls()
        server.login(os.environ['EMAIL_HOST_USER'], os.environ['EMAIL_HOST_PASSWORD'])
    print('SMTP authentication succeeded.')


if __name__ == '__main__':
    main()
