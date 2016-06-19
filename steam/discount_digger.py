import logging
import re
from typing import Sequence

import requests
from digger import Digger
from lxml import etree
from steam.model.game import SteamGame

logger = logging.getLogger(__name__)


class DiscountDigger(Digger):
    TABLE = 'steam_discount_game'

    @classmethod
    def run(cls, conn):
        discounted_games = cls._get_discounts()

        if not discounted_games:
            logger.error({
                'msg': 'Empty list of discount games. Abort.'
            })
            return

        cur = conn.cursor()
        try:
            # Clear table.
            cur.execute('TRUNCATE ' + cls.TABLE)
            # Order matters.
            cur.executemany("""
              INSERT INTO {} (
                name, link, img_src, review, price_before, price_now, discount)
              VALUES (%s, %s, %s, %s, %s, %s, %s)
            """.format(cls.TABLE), [g.to_tuple() for g in discounted_games])
            conn.commit()
        except Exception as e:
            # TODO: better notification.
            logger.error({
                'msg': 'Failed to insert discounted games to database.',
                'exception': str(e)
            })
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()

    @classmethod
    def _get_discounts(cls) -> Sequence[SteamGame]:
        discounts_url = (
            'http://store.steampowered.com/search/results?sort_by=Reviews_DESC&'
            'specials=1&page=1')

        # Output.
        games = []

        r = requests.get(discounts_url)
        html = etree.HTML(r.text)
        for row in html.xpath('//a[contains(@class, "search_result_row")]'):
            name = row.find('div/div/span[@class="title"]').text
            link = row.get('href')
            img_src = row.find('div/img').get('src')
            # HACK: change the image to larger ones.
            # .../capsule_sm_120.jpg?t=1465937731 -> .../capsule_616x353.jpg
            img_src_parts = img_src.split('/')
            if img_src_parts and 'capsule_sm_120' in img_src_parts[-1]:
                img_src_parts[-1] = 'capsule_616x353.jpg'
                img_src = '/'.join(img_src_parts)
            else:
                logger.warning({
                    'msg': 'Failed to substitute larger capsules',
                    'name': name,
                    'img_src': img_src,
                })

            review_ele = row.xpath(
                'div/div/span[contains(@class, "search_review_summary")]')
            if review_ele:
                review = review_ele[0].get('data-store-tooltip')
            else:
                review = ''

            # Order of non-empty texts: discount percentage, original price,
            # discounted price.
            q = 'div/div[contains(@class, "search_price_discount_combined")]'
            discount_info = []

            for text in row.xpath(q)[0].itertext():
                text = text.strip()
                if not text:
                    continue
                discount_info.append(text)

            if len(discount_info) != 3:
                logger.warning({
                    'msg': 'Malformed discount format',
                    'name': name,
                    'discount_info': str(discount_info)
                })
                continue
            # Price are shown as something like '$40.99'.
            price_before = float(discount_info[1][1:])
            price_now = float(discount_info[2][1:])

            price = SteamGame.Price(price_before, price_now)

            games.append(SteamGame(name, link, img_src, price, review))

        return games
