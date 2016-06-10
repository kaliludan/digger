import json
from flask import Flask
from steam.discounts_crawler import DiscountsCrawler
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
    
@app.route("/steam_discount")
def retrieve_steam_discount():
    crawler = DiscountsCrawler()
    discounts = crawler.get_discounts()
    return json.dumps(discounts)

if __name__ == "__main__":
    app.run()