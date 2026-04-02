class TransactionLogger:
    def log(self,message):
        print(f"[LOG]: {message}")

class Account:
    def __init__(self,name,balance):
        self.name=name
        self.__balance=balance
        self.logger=TransactionLogger()

    def deposit(self,amount):
        if amount <= 0:
            raise ValueError("invalid deposit amount")
        self.__balance +=amount
        print(f"Initial balance is {self.__balance}")
        self.logger=TransactionLogger()

    def withdraw(self,amount):
        if amount <=0:
            raise ValueError("Invalid withdraw amount")
        if amount > self.__balance:
            raise ValueError("Insufficient balance")
        self.__balance-=amount
        self.logger.log(f"{amount} withdrawn")

    def get_balance(self):
        return f"current balance: {self.__balance}"

acc=Account("john",1000)
acc.deposit(500)
acc.withdraw(200)
print(acc.get_balance())

