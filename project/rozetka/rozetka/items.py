# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class RozetkaItem(Item):
    title = Field()
    category = Field()
    description = Field()
    pass
