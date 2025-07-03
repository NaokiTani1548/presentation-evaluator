import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def send_notification_email(to_email: str, subject: str, body: str):
    """
    指定メールアドレスに通知メールを送信する関数。
    .envにSENDER_EMAIL, SENDER_NAME, SENDER_PASSWORD（アプリパスワード/Gmail推奨）を設定してください。
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv("SENDER_NAME", "AI Presentation Evaluator")
    sender_password = os.getenv("SENDER_PASSWORD")
    if not (sender_email and sender_password):
        print("メール送信設定が不足しています")
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], msg.as_string())
    except Exception as e:
        print(f"メール送信失敗: {e}")
