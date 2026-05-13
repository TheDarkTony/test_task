class ValidationRequestIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ValidationDataIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidPasswordValidationIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidStateIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ForbiddenAccessIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotFoundResourseIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)