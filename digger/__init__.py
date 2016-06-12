"""Base class for all crawlers."""


class Digger(object):
    @classmethod
    def run(cls, conn):
        """Run digger jobs to fetch data.

        :param conn: Database connection
        """
        raise NotImplementedError
