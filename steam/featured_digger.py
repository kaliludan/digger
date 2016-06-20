import asyncio
import logging
from typing import Dict

import aiohttp
from digger import Digger
from steam.model.game import SteamGame

logger = logging.getLogger(__name__)


class FeaturedDigger(Digger):
    TABLE = 'steam_featured_game'
    FEATURE_TYPES = [
        'large_capsules', 'featured_win', 'featured_mac', 'featured_linux']

    @classmethod
    async def run(cls, conn):
        feature_games = await cls._get_featured_games()

        if not feature_games:
            logger.error({
                'msg': 'Empty list of featured games. Abort.'
            })
            return

        async with conn.cursor() as cur:  # Auto commit.
            # Clear table
            await cur.execute('TRUNCATE ' + cls.TABLE)
            for feature, games in feature_games.items():
                tuples_to_insert = [g.to_tuple() + (feature,) for g in games]

                tasks, _ = await asyncio.wait([
                    cur.mogrify('(%s, %s, %s, %s, %s, %s, %s, %s)', t)
                    for t in tuples_to_insert])
                args_str = ','.join(f.result().decode("utf-8") for f in tasks)
                # Order matters
                query = """
                  INSERT INTO {} (
                    name, link, img_src, headline, price_before, price_now, discount, feature_type)
                  VALUES {}
                """.format(cls.TABLE, args_str)
                # http://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query
                # Seems single execute would be faster.
                await cur.execute(query)

    @classmethod
    async def _get_featured_games(cls) -> Dict[str, SteamGame]:
        featured_url = (
            'http://store.steampowered.com/api/featured/'
        )
        game_link_prefix = 'http://store.steampowered.com/app/'

        # Output.
        games = {}

        with aiohttp.ClientSession() as session:
            async with session.get(featured_url) as resp:
                json_response = await resp.json()

        for feature in cls.FEATURE_TYPES:
            feature_games = []
            raw_games = json_response[feature]
            # Massage game information and store in games.
            for raw_game in raw_games:
                original_price = raw_game['original_price']
                original_price = (
                    0.0 if not original_price else original_price / 100)
                final_price = raw_game['final_price'] / 100
                price = SteamGame.Price(original_price, final_price)
                link = game_link_prefix + str(raw_game['id'])

                game = SteamGame(
                    raw_game['name'], link, raw_game['large_capsule_image'],
                    price, raw_game.get('headline', ''))

                feature_games.append(game)

            games[feature] = feature_games

        return games
