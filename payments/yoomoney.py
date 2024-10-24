import logging
from yoomoney import Client, Quickpay
from typing import Tuple
from data.config import YOOMONEY_TOKEN, YOOMONEY_WALLET
from utils import generate_id

logger = logging.getLogger(__name__)


class AsyncYoomoneyAPI:
    def __init__(self, receiver: str = YOOMONEY_WALLET, token: str = YOOMONEY_TOKEN):
        """
        Creates instance of one Yoomoney API client

        Args:
            receiver: Receiver's wallet number or account
            YOOMONEY_TOKEN: Token from https://yoomoney.ru
        """
        self.receiver = receiver
        self.token = token

    async def create_payment(
        self,
        amount: float,
        targets: str = "Цифровая услуга",
        paymentType: str = "SB",
    ) -> Tuple[str, str]:
        """
        Creates payment URL

        Args:
            payment_id: Your payment id
            amount: Payment amount
            targets: Payment targets (Optional)
            paymentType: Payment type (Optional)

        Returns: Payment URL
        """
        payment_id = generate_id()
        quick_pay = Quickpay(
            receiver=self.receiver,
            quickpay_form="shop",
            targets=targets,
            paymentType=paymentType,
            sum=amount,
            label=payment_id,
        )
        return quick_pay.redirected_url, payment_id

    async def get_payment_info(self, payment_id: str):
        """
        Retrieves payment information

        Args:
            payment_id: Your payment ID

        Returns: JSON response with payment information
        """
        client = Client(self.token)
        try:
            history = client.operation_history(label=payment_id)
            if history.operations:
                return history.operations[-1]
            else:
                return None
        except Exception as e:
            logger.info(f"Error fetching payment info: {e}")
            return None

    async def is_expired(self, payment_id: str) -> bool:
        """Check if the payment is expired"""
        operation = await self.get_payment_info(payment_id)
        if operation is not None:
            return operation.status == "refused"
        return False

    async def is_success(self, payment_id: str) -> bool:
        """Check if the payment is successful"""
        operation = await self.get_payment_info(payment_id)
        return operation is not None and operation.status == "success"

    async def close(self) -> None:
        pass
