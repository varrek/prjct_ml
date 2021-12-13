# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class RozetkaItem(Item):
    title = Field()
    deep_category = Field()
    main_category = Field()
    deep_category_minus_one = Field()
    description = Field()
    pass
