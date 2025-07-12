import hashlib
import logging
from requests import post
from requests.exceptions import RequestException
from typing import Optional, Tuple
from data.config import AAIO_API_KEY, AAIO_SECRET_KEY, AAIO_MERCHANT_ID
from utils import generate_id

import aiohttp

AAIO_BALANCE_URL = "https://aaio.so"
logger = logging.getLogger(__name__)


class AsyncAaioAPI:
    def __init__(
        self,
        API_KEY: str = AAIO_API_KEY,
        SECRET_KEY: str = AAIO_SECRET_KEY,
        MERCHANT_ID: str = AAIO_MERCHANT_ID,
    ):
        """
        Creates instance of one AAIO merchant API client

        Args:
            merchant_id: Merchant ID from https://aaio.so/cabinet
            secret: 1st secret key from https://aaio.so/cabinet
            api_key: API key from https://aaio.so/cabinet/api
        """

        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.MERCHANT_ID = MERCHANT_ID
        self.name = "AAIO"

    async def create_payment(
        self,
        amount: float,
        lang: str | None = "ru",
        currency: str | None = "RUB",
        description: str | None = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """
        Creates payment URL
        See https://wiki.aaio.so/priem-platezhei/sozdanie-zakaza-zaprosom-rekomenduem for more detailed information

        Args:
            amount: Payment amount
            order_id: Your order id
            description: Payment description (Optional)
            currency: Payment currency
            language: Page language (Optional)

        Returns: Payment URL

        """
        payment_id = generate_id()
        merchant_id = self.MERCHANT_ID  # merchant id
        secret = self.SECRET_KEY  # secret key №1 from shop settings

        sign = ":".join(
            [str(merchant_id), str(amount), str(currency), str(secret), str(payment_id)]
        )

        payload = {
            "merchant_id": merchant_id,
            "amount": amount,
            "currency": currency,
            "order_id": payment_id,
            "sign": hashlib.sha256(sign.encode("utf-8")).hexdigest(),
            "desc": description,
            "lang": lang,
        }

        headers = {"Accept": "application/json"}

        try:
            response = post(
                "https://aaio.so/merchant/get_pay_url",
                headers=headers,
                data=payload,
                timeout=(15, 60),
            )
            response.raise_for_status()  # Проверка статуса ответа
        except RequestException as e:
            logger.info(f"Connect error: {e}")
            raise RequestException

        # Проверка кода ответа
        if response.status_code not in [200, 400, 401]:
            logger.info(f"Response code: {response.status_code}")
            raise RequestException

        try:
            decoded = response.json()  # Парсинг результата
        except ValueError:
            logger.info("Unable to decode JSON response")
            raise ValueError

        if decoded.get("type") == "success":
            return decoded["url"], payment_id
        else:
            logger.info(f"Error: {decoded.get('message', 'Unknown error')}")
            raise ValueError

    async def get_payment_info(self, order_id):
        """
        Creates a request for get payment information
        See https://wiki.aaio.so/api/informaciya-o-zakaze

        Args:
            order_id: Your order ID

        Returns: Model from response JSON

        """

        URL = "https://aaio.so/api/info-pay"

        params = {"merchant_id": self.MERCHANT_ID, "order_id": order_id}

        headers = {"Accept": "application/json", "X-Api-Key": self.API_KEY}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(URL, data=params) as response:
                response_json = await response.json()

                return response_json

    async def is_success(self, order_id):
        """Check status payment (success)"""

        response_json = await self.get_payment_info(order_id)
        # print(response_json)

        return (
            response_json["type"] == "success" and response_json["status"] == "success"
        ) or (response_json["type"] == "success" and response_json["status"] == "hold")

    async def close(self) -> None:
        pass

    async def get_balance(self) -> Optional[dict[str, str]]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Api-Key": self.API_KEY,
        }

        try:
            async with aiohttp.ClientSession(AAIO_BALANCE_URL) as session:
                async with session.post("/api/balance", headers=headers) as r:
                    response = await r.json(content_type=None)
                    if response["type"] == "success":
                        return {"RUB": str(response["balance"])}
                    else:
                        logger.info(f"Error fetching balance: {response}")
                        return None
        except Exception as e:
            logger.info(f"Exception while fetching balance: {e}")
            return None
