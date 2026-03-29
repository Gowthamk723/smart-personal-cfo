from enum import Enum


class FinancialType(str, Enum):
    income = "income"
    expense = "expense"
