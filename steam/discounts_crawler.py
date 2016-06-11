import logging
import re

import requests
from lxml import etree

from crawler import Crawler

logger = logging.getLogger('digger.steam.discount_crawler')

STEAM_MAX_RETRIEVAL_BATCH = 10


class SteamGame(object):
    """All fields are strings."""

    class Price(object):
        def __init__(self, discount_str, price_before_str, price_now_str):
            self.discount = discount_str
            self.price_before = float(price_before_str[1:])
            self.price_now = float(price_now_str[1:])

        def __repr__(self):
            return '${} -> ${}'.format(self.price_before, self.price_now)

    def __init__(self, name, link, img_src, price, review):
        self.name = name
        self.link = link
        self.img_src = img_src
        self.price = price
        self.review = review


class DiscountsCrawler(Crawler):
    @classmethod
    def run(cls):
        # TODO: add persistence methods.
        discounted_games = cls._get_discounts()
        for game in discounted_games:
            print(game.__dict__)

    @classmethod
    def _crawl_discounts(cls):
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
                logger.warn({
                    'msg': 'Malformed discount format',
                    'name': name,
                    'discount_info': str(discount_info)
                })
                continue

            price = SteamGame.Price(*discount_info)

            games.append(SteamGame(name, link, img_src, price, review))

        return games

    @classmethod
    def _get_num_discounts(cls):
        page = requests.get(
            'http://store.steampowered.com/search/?specials=1').text
        mo = re.search(r'showing.*of +(\d+)', page)
        if mo is not None:
            return int(mo.group(1))

    @classmethod
    def _get_discounts(cls):
        # TODO: may need more games in the future.
        return cls._crawl_discounts()
