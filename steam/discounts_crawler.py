import os
import re
import subprocess
import sys
import urllib
import HTMLParser
import htmlentitydefs
import itertools

class Entry(object):
    def __init__(self):
        self.title = u''
        self.orig_price = u''
        self.discount = u''
        self.price = u''

    # Entries can be sorted by title.
    def __cmp__(self, other):
        return cmp(self.title.lower(), other.title.lower())
    
class DiscountsParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
    
    @staticmethod
    def entity2uni(name):
        return unichr(htmlentitydefs.name2codepoint[name])

    @staticmethod
    def ref2uni(ref):
        return unichr(int(ref))

    def reset(self):
        HTMLParser.HTMLParser.reset(self)

        self.current_entry_ = None
        self.entries_ = []

        self.in_h4_ = False
        self.in_discount_pct_ = False
        self.in_tab_price_ = False
        self.in_strike_ = False

    def handle_starttag(self, tag, attrs):
        attrs_map = dict(attrs)

        if tag == 'h4':
            # First field to extract, hence new entry.
            self.in_h4_ = True
            self.current_entry_ = Entry()

        elif tag == 'div':
            if attrs_map.get('class', '') == 'tab_discount discount_pct':
                self.in_discount_pct_ = True
            elif attrs_map.get('class', '') == 'tab_price':
                self.in_tab_price_ = True

        elif tag == 'strike':
            self.in_strike_ = True
    
    def handle_endtag(self, tag):
        if tag == 'h4':
            self.in_h4_ = False

        elif tag == 'div':
            if self.in_discount_pct_:
                self.in_discount_pct_ = False
            elif self.in_tab_price_:
                self.in_tab_price_ = False
                # This was the last field to extract.
                self.entries_.append(self.current_entry_)

        elif tag == 'strike':
            self.in_strike_ = False

    def append_text(self, text):
        if self.in_h4_:
            self.current_entry_.title += text
        elif self.in_discount_pct_:
            self.current_entry_.discount += text
        elif self.in_strike_:
            self.current_entry_.orig_price += text
        elif self.in_tab_price_:
            # Note we only enter here if not in <strike>.
            self.current_entry_.price += text

    def handle_data(self, data):
        self.append_text(data.strip().decode('utf-8'))
    
    def handle_entityref(self, name):
        self.append_text(self.entity2uni(name))
    
    def handle_charref(self, ref):
        self.append_text(self.ref2uni(ref))
    
    # Behave like a sequence of Entries.
    def __len__(self):
        return self.entries_.__len__()

    def __getitem__(self, key):
        return self.entries_.__getitem__(key)

    def __iter__(self):
        return self.entries_.__iter__()

    def __reversed__(self):
        return self.entries_.__reversed__()

    def __contains__(self, item):
        return self.entries_.__contains__(item)

class DiscountsCrawler:
    
    def __init__(self):
        self.MAX_BATCH_SIZE = 50
    
    def get_num_discounts(self):
        # Get the number of discounts first.
        conn = urllib.urlopen('http://store.steampowered.com/search/?specials=1')
        page = conn.read()
        conn.close()
        mo = re.search(r'showing.*of +(\d+)', page)
        if mo is not None:
            return int(mo.group(1))
    
    def crawl_discounts(self, start, batch_size):
        discounts_url = \
            'http://store.steampowered.com/search/tab?bHoverEnabled=true&' + \
            'style=&navcontext=1_4_4_&tab=Discounts&start=%d&count=%d' % \
            (start, batch_size)

        conn = urllib.urlopen(discounts_url)
        page = conn.read()
        conn.close()

        # Parse discounts.
        discounts_parser = DiscountsParser()
        discounts_parser.feed(page)
        
        return discounts_parser
    
    def get_discounts(self):
        remaining = self.get_num_discounts()
        batches = []
        discounts = []
        start = 0
        while remaining > 0:
            batch_size = min(remaining, self.MAX_BATCH_SIZE)
            batch = self.crawl_discounts(start, batch_size)
            received_size = len(batch)
            start += received_size
            remaining -= received_size
            batches.append(batch)
            if received_size < batch_size:
                break
        for entry in sorted(itertools.chain(*batches)):
            discount = {}
            discount['title'] = entry.title
            discount['price'] = entry.price
            discount['origin_price'] = entry.orig_price,
            discount['discount'] = entry.discount
            discounts.append(discount)
            
        return discounts
            
            