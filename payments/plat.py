import logging
import aiohttp
import json
import hashlib
from typing import Literal, Optional, Tuple, Any

from data.config import (
    PLAT_MERCHANT_ID,
    PLAT_SECRET_KEY,
    PLAT_API_URL,
)
from utils import generate_id

logger = logging.getLogger(__name__)
CREATE_PAYMENT_URL = "/api/merchant/order/create/by-api"


class AsyncPlatAPI:
    def __init__(
        self,
        merchant_id: str = PLAT_MERCHANT_ID,
        secret_key: str = PLAT_SECRET_KEY,
        base_url: str = PLAT_API_URL,
        method: Literal["card", "sbp", "crypto", "qr"] = "sbp",
        **kwargs,
    ):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.method = method
        self.name = "PlatCash"

    def _generate_sign(self, amount: int | float, merchant_order_id: str) -> str:
        """
        md5(shop_id + ':' + secret + ':' + amount + ':' + merchant_order_id)
        """
        sign_str = f"{self.merchant_id}:{self.secret_key}:{amount}:{merchant_order_id}"
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest()

    async def create_payment(
        self,
        amount: int | float,
        user_id: int,
        currency: str = "RUB",
    ) -> Tuple[str, str]:
        method = self.method

        merchant_order_id = generate_id()

        payload = {
            "merchant_order_id": merchant_order_id,
            "user_id": user_id,
            "shop_id": int(self.merchant_id),
            "amount": amount,
            "method": method,
        }

        if method == "crypto":
            payload["currency"] = currency

        headers = {
            "Content-Type": "application/json",
            "x-shop": str(self.merchant_id),
            "x-secret": self.secret_key,
        }

        url = f"{self.base_url}{CREATE_PAYMENT_URL}"
        logger.info(f"Sending create payment request: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, data=json.dumps(payload)
            ) as response:
                text = await response.text()

                if response.status != 200:
                    logger.error(f"Create payment failed [{response.status}]: {text}")
                    return "ERROR", "ERROR"

                try:
                    data = json.loads(text)
                    print(data)
                    guid = data["payment"]["guid"]
                    pay_url = data["url"]
                    logger.info(f"Created payment: guid={guid}, url={pay_url}")
                    return pay_url, guid
                except Exception as e:
                    logger.exception(f"[Plat] Failed to parse response: {text}")
                    raise e

    async def get_payment_info(self, guid: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/merchant/order/info/{guid}/by-api"
        logger.info(f"Fetching payment info for GUID: {guid}")

        headers = {
            "Content-Type": "application/json",
            "x-shop": str(self.merchant_id),
            "x-secret": self.secret_key,
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Error fetching info [{response.status}]: {text}")
                    raise Exception(
                        f"Error fetching info for {guid}: {response.status} {text}"
                    )
                data = await response.json()
                logger.info(f"Payment info: {data}")
                return data

    async def is_success(self, guid: str) -> bool:
        data = await self.get_payment_info(guid)
        status = data.get("payment", {}).get("status")
        is_successful = status in (1, 2)

        logger.info(
            f"Status check for {guid}: {status} → {'SUCCESS' if is_successful else 'NOT SUCCESS'}"
        )
        return is_successful

    async def close(self):
        pass

    async def get_balance(self) -> Optional[dict[str, str]]:
        url = f"{PLAT_API_URL}/api/shop/info/by-api"
        headers = {
            "Content-Type": "application/json",
            "x-shop": str(PLAT_MERCHANT_ID),
            "x-secret": PLAT_SECRET_KEY,
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.info(
                            f"Error fetching shop info [{response.status}]: {text}"
                        )
                        return None
                    data = await response.json()
                    return {"RUB": str(data["shop"]["balance"])}
        except Exception as e:
            logger.exception(f"Exception while fetching balance: {e}")
            return None
