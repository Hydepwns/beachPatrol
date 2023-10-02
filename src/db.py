class DB:
    def __init__(self):
        self.watchlist = []
        self.whitelist = []

    def add_to_watchlist(self, item):
        self.watchlist.append(item)

    def remove_from_watchlist(self, item):
        self.watchlist.remove(item)

    def get_watchlist(self):
        return self.watchlist

    def add_to_whitelist(self, item):
        self.whitelist.append(item)

    def remove_from_whitelist(self, item):
        self.whitelist.remove(item)

    def get_whitelist(self):
        return self.whitelist
