class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.status_code = status_code
        self.status_code = "error"
        self.message = message
        