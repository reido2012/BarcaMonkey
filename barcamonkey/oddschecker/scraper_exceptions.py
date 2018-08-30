class BannedException(Exception):
    def __init__(self, msg=None):
        self.msg = ""

        if msg is None:
            self.msg = "Scraper has been banned from website! Please wait or use VPN."

        super(Exception, self).__init__(self.msg)


class Exception404(Exception):
    def __init__(self, msg=None):
        self.msg = ""

        if msg is None:
            self.msg = "URL is broken. Page can not be found."

        super(Exception, self).__init__(self.msg)