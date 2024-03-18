class Person:
    def __init__(self, name: str, expenses: dict):
        self.name = name.upper()
        self.expenses = expenses

        # Credit = you spent more than the split amount
        self.credit = 0

        # Debt is how much you owe
        self.debt = 0

        # Used for calculating repayments
        self.final_balance = 0


    def add_credit(self, amount: float) -> float:
        self.credit += amount


    def add_debt(self, amount: float) -> float:
        self.debt += amount


    def set_final_balance(self) -> float:
        self.final_balance = self.credit - self.debt


    def balance(self) -> float:
        return self.credit - self.debt


    def in_debt(self) -> bool:
        if (self.credit - self.debt) < 0:
            return True
        else:
            return False
