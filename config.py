from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env", override=True)

# ENOT
ENOT_API_KEY = os.getenv("ENOT_API_KEY")
ENOT_API_URL = "https://enot.ai.mono.t3zt.com/api/3a"

# Google Ads
DEVELOPER_TOKEN = os.getenv("DEVELOPER_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
CUSTOMER_ID = os.getenv("CUSTOMER_ID")

# Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "keyword_data"
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
# On Render: content of the JSON file as a string (takes priority)
SERVICE_ACCOUNT_JSON_CONTENT = os.getenv("SERVICE_ACCOUNT_JSON_CONTENT")

# Keyword settings
BRAND_VARIATIONS = [
    "монобанк", "моно", "monobank", "mono",
    "монобанку", "моні", "монобізнес", "monoбізнес", "моно бізнес", "mono бізнес"
]

PRODUCT_KEYWORDS = {
    "еквайринг": [
        "еквайринг", "эквайринг", "acquiring",
        "pos", "термінал", "прийом карток",
        "оплата картками", "еквайрінг"
    ],
    "рахунок_фоп": [
        "рахунок фоп", "рахунок підприємця",
        "фоп", "рахунок фізособи підприємця",
        "бізнес рахунок фоп"
    ],
    "зарплатний_проєкт": [
        "зарплатний проєкт", "зарплатний проект",
        "зп проєкт", "зарплата співробітникам",
        "виплата зарплати"
    ],
    "юррахунок": [
        "юррахунок", "рахунок тов",
        "рахунок для бізнесу", "бізнес рахунок"
    ],
}
