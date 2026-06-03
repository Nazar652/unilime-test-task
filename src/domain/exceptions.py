class MailError(Exception):
    ...


class EmailNotReadyError(MailError):
    ...


class MailboxTimeoutError(MailError):
    ...


class MessageNotFoundError(MailError):
    ...
