import asyncio
import os
from urllib.parse import urlparse

import aiopg
from steam.discount_digger import DiscountDigger
from steam.featured_digger import FeaturedDigger


async def get_db_conn():
    if os.getenv('ENV') == 'HEROKU':
        # On production Heroku.
        url = urlparse(os.environ["DATABASE_URL"])
        db_conn = await aiopg.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # Local dev.
        db_conn = await aiopg.connect(
            database='bot',
            client_encoding='utf8',
        )
    return db_conn

async def main():
    conn = await get_db_conn()
    tasks = [
        DiscountDigger.run(conn),
        FeaturedDigger.run(conn)]
    await asyncio.wait(tasks)
    conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
