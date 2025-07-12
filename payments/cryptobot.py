import logging
from aiocryptopay import AioCryptoPay, Networks
from typing import Tuple, Optional

from data.config import CRYPTO_BOT_TOKEN

logger = logging.getLogger(__name__)


class AsyncCryptoPayAPI:
    def __init__(
        self, token: str = CRYPTO_BOT_TOKEN, network: Networks = Networks.MAIN_NET
    ):
        """
        Creates instance of one CryptoPay merchant API client

        Args:
            token: API token from CryptoPay
            network: Network type (MAIN_NET or TEST_NET)
        """
        self.crypto = AioCryptoPay(token=token, network=network)
        self.name = "CryptoBot"

    async def create_payment(
        self, amount: float, currency: str = "RUB", **kwargs
    ) -> Tuple[str, str]:
        """
        Creates payment URL

        Args:
            amount: Payment amount
            currency: Payment currency (default is RUB)

        Returns: Payment URL
        """
        invoice = await self.crypto.create_invoice(
            amount=float(amount), fiat=currency, currency_type="fiat"
        )
        return invoice.bot_invoice_url, str(invoice.invoice_id)

    async def is_success(self, invoice_id: str) -> bool:
        """Check if the payment is successful"""
        invoice_info = await self.crypto.get_invoices(invoice_ids=int(invoice_id))
        return invoice_info.status == "paid"

    async def close(self):
        await self.crypto.close()

    async def get_balance(self) -> Optional[dict[str, str]]:
        try:
            balances = await self.crypto.get_balance()
            output = {}

            for balance in balances:
                if balance.available > 0:
                    output[balance.currency_code] = str(balance.available)

            return output if output else None
        except Exception as e:
            logger.exception(f"Failed to get balance: {e}")
            return None
        finally:
            await self.crypto.close()
