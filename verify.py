import requests

from config import MAIN_BOT_API, API_KEY


def verify_user(ad_id: int, user_id: int):

    data = {
        "api_key": API_KEY,
        "ad_id": ad_id,
        "user_id": user_id
    }

    try:

        r = requests.post(
            MAIN_BOT_API,
            json=data,
            timeout=10
        )

        return r.json()

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }