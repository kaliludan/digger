class SteamGame(object):

    class Price(object):
        """Lightweight wrapper for discounted price."""

        def __init__(self, price_before: float, price_now: float):
            self.price_before = price_before  # type: float
            self.price_now = price_now  # type: float

        def __repr__(self):
            return '${} -> ${}'.format(self.price_before, self.price_now)

        @property
        def discount(self):
            # May not be a discounted game.
            if not self.price_before:
                return 0.0
            # Calculated as the 1 - <now> / <before>.
            return round(1 - self.price_now / self.price_before, ndigits=2)

    def __init__(self, name: str, link: str, img_src: str,
                 price: Price, description: str):
        self.name = name  # type: str
        self.link = link  # type: str
        self.img_src = img_src  # type: str
        self.price = price  # type: SteamGame.Price
        self.description = description  # type: str

    def to_tuple(self):
        # Order matters.
        return (
            self.name, self.link, self.img_src, self.description,
            self.price.price_before, self.price.price_now, self.price.discount)
