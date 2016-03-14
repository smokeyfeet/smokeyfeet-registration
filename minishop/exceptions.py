class MinishopException(IOError):
    pass


class ProductError(MinishopException):
    pass


class CartError(MinishopException):
    pass
