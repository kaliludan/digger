import json
import logging
from typing import Dict

import requests
from digger import Digger
from steam.model.game import SteamGame

logger = logging.getLogger(__name__)


class FeaturedDigger(Digger):
    TABLE = 'steam_featured_game'
    FEATURE_TYPES = [
        'large_capsules', 'featured_win', 'featured_mac', 'featured_linux']

    @classmethod
    def run(cls, conn):
        feature_games = cls._get_featured_games()

        if not feature_games:
            logger.error({
                'msg': 'Empty list of featured games. Abort.'
            })
            return

        cur = conn.cursor()
        try:
            # Clear table
            cur.execute('TRUNCATE ' + cls.TABLE)
            for feature, games in feature_games.items():
                tuples_to_insert = [g.to_tuple() + (feature,) for g in games]
                # Order matters
                cur.executemany("""
                  INSERT INTO {} (
                    name, link, img_src, headline, price_before, price_now, discount, feature_type)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """.format(cls.TABLE), tuples_to_insert)
            conn.commit()
        except Exception as e:
            logger.error({
                'msg': 'Failed to insert featured games to database.',
                'exception': str(e)
            })
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()

    @classmethod
    def _get_featured_games(cls) -> Dict[str, SteamGame]:
        feature_url = (
            'http://store.steampowered.com/api/featured/'
        )
        game_link_prefix = 'http://store.steampowered.com/app/'

        # Output.
        games = {}

        response = requests.get(feature_url)
        json_response = json.loads(response.text)

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
