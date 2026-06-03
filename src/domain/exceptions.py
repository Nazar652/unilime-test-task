class MailError(Exception):
    ...


class EmailNotReadyError(MailError):
    ...


class MailboxTimeoutError(MailError):
    ...


class ProviderUnavailableError(MailError):
    ...


class MessageNotFoundError(MailError):
    ...
