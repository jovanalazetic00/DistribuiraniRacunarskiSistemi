# Online account to bank account

class Transaction2:
    def __init__(self, transactionId, sender, receiverCardNumber, senderAmount, conversionRates, currency) -> None:
        self.transactionId = transactionId
        self.sender = sender
        self.receiverCardNumber = receiverCardNumber
        self.senderAmount = senderAmount
        self.conversionRates = conversionRates
        self.currency = currency
