class Payment:
    def pay(self,amount):
        pass
class UPI(Payment):
    def pay(self,amount):
        print("payment successful via UPI")
class Card(Payment):
    def pay(self,amount):
        print("payment sucsessful via card")
class Discount:
    def apply(self,amount):
        return amount
class FestivalDiscount(Discount):
    def apply(self,amount):
        return amount * 0.9
class PremiumDiscount(Discount):
    def apply(self,amount):
        return amount * 0.8
class Logger:
    def log(self,message):
        print(f"[LOG]:{message}")
class Checkout:
    def __init__(self,payment:Payment,discount:Discount):
        self.payment=payment
        self.discount=discount
        self.logger=Logger()
    def process(self,amount):
        final_amount=self.discount.apply(amount)
        print(f"final amount : {int(final_amount)}")
        self.payment.pay(final_amount)
        self.logger.log("Checkout completed")
checkout=Checkout(payment=UPI(),discount=FestivalDiscount())
checkout.process(1000)