class MinishopException(Exception):
    pass


class CartFullError(MinishopException):
    pass


class StockOutError(MinishopException):
    pass
