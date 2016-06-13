import os
from urllib.parse import urlparse

import psycopg2
from steam.discount_digger import DiscountDigger


def get_db_conn():
    if os.getenv('ENV') == 'HEROKU':
        # On production Heroku.
        url = urlparse(os.environ["DATABASE_URL"])
        db_conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # Local dev.
        db_conn = psycopg2.connect(
            database='bot',
            client_encoding='utf8',
        )
    return db_conn

if __name__ == "__main__":
    conn = get_db_conn()

    # Run different data source fetching jobs.
    DiscountDigger.run(conn)

    conn.close()
