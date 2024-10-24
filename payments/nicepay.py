import aiohttp
import secrets
import random
import json
from typing import Literal, Tuple
from utils import generate_id
from data.config import db, NICE_PAY_MERCHANT_ID, NICE_PAY_SECRET_KEY


class AsyncNicePayAPI:
    def __init__(
        self,
        SECRET_KEY: str = NICE_PAY_SECRET_KEY,
        MERCHANT_ID: str = NICE_PAY_MERCHANT_ID,
    ):
        """
        Creates instance of one NicePay merchant API client

        Args:
            merchant_id: Merchant ID
            secret: 1st secret key
        """

        self.secret_key = SECRET_KEY
        self.merchant_id = MERCHANT_ID

    async def create_payment(
        self,
        amount: float,
        currency: Literal["USD", "EUR", "RUB", "UAH", "KZT"] | None = "RUB",
        description: str | None = None,
        success_url: str | None = None,
        fail_url: str | None = None,
    ) -> Tuple[str, str]:
        payment_id = generate_id()
        customer = f"{secrets.token_hex(random.randint(5, 10))}@mail.ru"
        url = "https://nicepay.io/public/api/payment"
        headers = {"Content-Type": "application/json"}
        payload = {
            "merchant_id": self.merchant_id,
            "secret": self.secret_key,
            "order_id": payment_id,
            "customer": customer,
            "amount": amount * 100,
            "currency": currency,
        }
        if description:
            payload["description"] = description
        if success_url:
            payload["success_url"] = success_url
        if fail_url:
            payload["fail_url"] = fail_url

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, data=json.dumps(payload)
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("status") == "success":
                        return response_data["data"]["link"], payment_id
                    else:
                        raise Exception(f"Error in response: {response_data}")
                else:
                    raise Exception(f"HTTP Error: {response.status}")

    async def is_expired(self, payment_id: str) -> bool:
        """Check if the payment is expired"""
        payment = await db.payments_api.get_payment_info(db.session_maker, payment_id)
        return payment is not None and payment.status == "expired"

    async def is_success(self, payment_id: str) -> bool:
        """Check if the payment is successful"""
        payment = await db.payments_api.get_payment_info(db.session_maker, payment_id)
        return payment is not None and payment.status == "successful"

    async def close(self):
        pass
