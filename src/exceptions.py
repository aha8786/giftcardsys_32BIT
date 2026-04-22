class GiftCardError(Exception):
    pass


class DuplicateBarcodeError(GiftCardError):
    def __init__(self, barcode: str):
        super().__init__(f"이미 등록된 바코드입니다: {barcode}")
        self.barcode = barcode


class CardNotFoundError(GiftCardError):
    def __init__(self, barcode: str):
        super().__init__(f"등록되지 않은 카드입니다: {barcode}")
        self.barcode = barcode


class InsufficientBalanceError(GiftCardError):
    def __init__(self, balance: int, amount: int):
        super().__init__(f"잔액이 부족합니다. 현재 잔액: {balance:,}원, 결제 금액: {amount:,}원")
        self.balance = balance
        self.amount = amount


class InvalidAmountError(GiftCardError):
    def __init__(self, value):
        super().__init__(f"올바르지 않은 금액입니다: {value}")
        self.value = value


class InvalidBarcodeError(GiftCardError):
    def __init__(self, value):
        super().__init__(f"올바르지 않은 바코드입니다: {value}")
        self.value = value


class DatabaseConnectionError(GiftCardError):
    def __init__(self, detail: str = ""):
        msg = "데이터베이스 연결에 실패했습니다."
        if detail:
            msg += f" ({detail})"
        super().__init__(msg)
