import unittest

from steam.discount_digger import SteamGame, DiscountDigger


class TestSteamGame(unittest.TestCase):

    def test_to_tuple(self):
        price = SteamGame.Price('-10% ', '$9.99', '$8.99')
        game = SteamGame('name', 'link', 'img_src', price, 'review')
        t = game.to_tuple()
        self.assertEqual(
            t, ('name', 'link', 'img_src', 'review', 9.99, 8.99, '-10% '))


class TestDiscountDigger(unittest.TestCase):
    # TODO: add fixtures.
    pass
