import os

DB_PATH = os.getenv("GIFTCARD_DB_PATH", "giftcard.db")
BACKUP_DIR = os.getenv("GIFTCARD_BACKUP_DIR", "backups")
LOG_PATH = os.getenv("GIFTCARD_LOG_PATH", "giftcard.log")

LOW_BALANCE_THRESHOLD = int(os.getenv("LOW_BALANCE_THRESHOLD", "1000"))

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "")
KAKAO_SENDER_KEY = os.getenv("KAKAO_SENDER_KEY", "")
KAKAO_TEMPLATE_CODE_REGISTER = os.getenv("KAKAO_TEMPLATE_CODE_REGISTER", "")
KAKAO_TEMPLATE_CODE_CHARGE = os.getenv("KAKAO_TEMPLATE_CODE_CHARGE", "")
KAKAO_TEMPLATE_CODE_PAYMENT = os.getenv("KAKAO_TEMPLATE_CODE_PAYMENT", "")
KAKAO_API_URL = "https://kakaoapi.aligo.in/akv10/alimtalk/send/"
