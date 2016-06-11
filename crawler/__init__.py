"""Base class for all crawlers."""


class Crawler(object):
    @classmethod
    def run(cls):
        raise NotImplementedError
