import uuid

from faker import Faker

fake = Faker()


class UserFactory:
    @staticmethod
    def build(email: str = None, password: str = "PassWord123!", full_name: str = None, phone: str = None) -> dict:
        uid = uuid.uuid4().hex[:8]
        return {
            "email": email or f"qa_user_{uid}@testfinpay.io",
            "password": password,
            "full_name": full_name or fake.name(),
            "phone": phone or fake.phone_number()[:15],
        }


class CardFactory:
    @staticmethod
    def build(cardholder_name: str = None, card_type: str = "VIRTUAL", spending_limit: float = 1000.0) -> dict:
        return {
            "cardholder_name": cardholder_name or fake.name().upper(),
            "card_type": card_type,
            "spending_limit": spending_limit,
        }


class TransferFactory:
    @staticmethod
    def build(
        receiver_email: str,
        amount: float = 50.0,
        currency: str = "USD",
        description: str = None,
        idempotency_key: str = None
    ) -> dict:
        uid = uuid.uuid4().hex[:10]
        return {
            "receiver_email": receiver_email,
            "currency": currency,
            "amount": amount,
            "description": description or f"QA Automated Transfer {uid}",
            "idempotency_key": idempotency_key or f"idem_{uid}",
        }
