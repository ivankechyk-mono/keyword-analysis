import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from config import DEVELOPER_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, CUSTOMER_ID


def get_client() -> GoogleAdsClient:
    credentials = {
        "developer_token": DEVELOPER_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(credentials)


def get_customer_id() -> str:
    return CUSTOMER_ID.replace("-", "")


def test_connection():
    client = get_client()
    customer_id = get_customer_id()
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT customer.id, customer.descriptive_name
        FROM customer
        LIMIT 1
    """
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            print(f"Connected: {row.customer.descriptive_name} (ID: {row.customer.id})")
        return True
    except GoogleAdsException as e:
        print(f"Google Ads API error: {e.error.code().name}")
        for error in e.failure.errors:
            print(f"  {error.message}")
        return False


if __name__ == "__main__":
    test_connection()
