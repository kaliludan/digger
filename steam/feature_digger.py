import json
import logging
import requests

from typing import Sequence

from digger import Digger
from steam.discount_digger import SteamGame

logger = logging.getLogger(__name__)


class FeatureDigger(Digger):
    
    table = 'steam_feature_game'
    CAPSULE = 'large_capsules'
    WIN = 'featured_win'
    MAC = 'featured_mac'
    LINUX = 'featured_linux'
    feature_types = [CAPSULE, WIN, MAC, LINUX] 

    @classmethod
    def run(cls, conn):
        feature_games = cls._get_features()

        if not feature_games:
            logger.error({
                'msg': 'Empty list of discount games. Abort.'
            })
            return

        cur = conn.cursor()
        try:
            # Clear table
            cur.execute('TRUNCATE ' + cls.table)
            for feature in feature_games:
                games = feature_games[feature]
                # Order matters
                cur.executemany("""
                  INSERT INTO {} (
                    name, link, img_src, review, price_before, price_now, discount, feature_type)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """.format(cls.table), [g.to_tuple() + (feature,) for g in games])
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
    def _get_features(cls) -> Sequence[SteamGame]:
        feature_url = (
            'http://store.steampowered.com/api/featured/'
        )
        game_link = ''
        
        #Output
        games = {}

        response = requests.get(feature_url)
        json_response = json.loads(response.text)

        for feature in cls.feature_types:
            feature_games = []
            raw_games = json_response[feature] 
            # Massage game information and store in games
            for raw_game in raw_games:
                discount_percent = raw_game['discount_percent']/100.0
                original_price = raw_game['original_price'] 
                original_price = 0.0 if not original_price else original_price/100.0
                final_price = raw_game['final_price']/100.0
                price = SteamGame.Price(str(discount_percent), 
                                        '$'+str(original_price), 
                                        '$'+str(final_price)
                                       )
                link = game_link + str(raw_game['id'])
                feature_games.append(SteamGame(raw_game['name'], link, raw_game['large_capsule_image'],
                                      price, raw_game.get('headline', '')))
            games[feature] = feature_games
            
        return games
