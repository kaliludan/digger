import unittest

from steam.discount_digger import DiscountDigger
from steam.model.game import SteamGame


class TestSteamGame(unittest.TestCase):

    def test_to_tuple(self):
        price = SteamGame.Price(9.99, 8.99)
        game = SteamGame('name', 'link', 'img_src', price, 'review')
        t = game.to_tuple()
        self.assertEqual(
            t, ('name', 'link', 'img_src', 'review', 9.99, 8.99, 0.1))
