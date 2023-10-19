# Online account to online account

class Transaction1:
    def __init__(self, transactionId, sender, receiver, senderAmount, conversionRates, currency) -> None:
        self.transactionId = transactionId
        self.sender = sender
        self.receiver = receiver
        self.senderAmount = senderAmount
        self.conversionRates = conversionRates
        self.currency = currency
