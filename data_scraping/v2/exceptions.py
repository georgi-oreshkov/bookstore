class RequestException(Exception):
    def __init__(self, message):
        self.message = message


class CoverMissingException(Exception):
    def __init__(self):
        pass


class AuthorMissingException(Exception):
    def __init__(self, message):
        self.message = message
        pass


class AuthorImgMissingException(Exception):
    def __init__(self):
        pass
