from bs4 import BeautifulSoup
from rozetka.items import RozetkaItem
from scrapy import Spider, Request


class RozetkaSpider(Spider):
    name = 'rozetka'
    allowed_domains = ['rozetka.com.ua']
    start_urls = ['https://rozetka.com.ua/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.declare_xpath()

    def declare_xpath(self):
        self.get_all_categories_xpath = '/html/body/app-root/div/div/rz-main-page/div/aside/main-page-sidebar/sidebar-fat-menu/div/ul/li/a/@href'
        self.get_all_sub_categories_xpath = '/html/body/app-root/div/div/rz-super-portal/div/main/section/div/rz-dynamic-widgets/rz-widget-list/section/ul/li/rz-list-tile/div/a[1]/@href'
        self.get_all_items_xpath = '/html/body/app-root/div/div/rz-category/div/main/rz-catalog/div/div/section/rz-grid/ul/li/app-goods-tile-default/div/div[2]/a[2]/@href'
        self.title_xpath = '/html/body/app-root/div/div/rz-product/div/rz-product-top/div/div[1]/h1'
        self.description_xpath = '//*[@id="#scrollArea"]/div[2]/div[1]/app-text-content/div/div'
        self.category_xpath = '/html/body/app-root/div/div/rz-product/div/rz-product-top/div/app-breadcrumbs/ul/li[4]/a/span'
        self.next_page_xpath = '/html/body/app-root/div/div/rz-category/div/main/rz-catalog/div/div/section/rz-catalog-paginator/app-paginator/div/a[2]/@href'

    def parse(self, response, **kwargs):
        for href in response.xpath(self.get_all_categories_xpath):
            url = response.urljoin(href.extract())
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        for href in response.xpath(self.get_all_sub_categories_xpath):
            url = response.urljoin(href.extract())
            yield Request(url, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        for href in response.xpath(self.get_all_items_xpath):
            url = response.urljoin(href.extract())
            yield Request(url, callback=self.parse_main_item)

        next_page = response.xpath(self.next_page_xpath).extract_first()
        if next_page is not None:
            url = response.urljoin(next_page)
            yield Request(url, callback=self.parse_subcategory, dont_filter=True)

    def parse_main_item(self, response):
        item = RozetkaItem()

        title = response.xpath(self.title_xpath).extract()
        title = self.process_xpath_elemnt(title)

        category = response.xpath(self.category_xpath).extract()
        category = self.process_xpath_elemnt(category)

        description = response.xpath(self.description_xpath).extract()
        description = self.process_xpath_elemnt(description)

        # Put each element into its item attribute.
        item['title'] = title
        item['category'] = category
        item['description'] = description
        return item

    def process_xpath_elemnt(self, element):
        element = self.listToStr(element)
        element = self.remove_tags(element)

        return element

    def listToStr(self, MyList):
        dumm = ""
        MyList = [i for i in MyList]
        for i in MyList: dumm = "{0}{1}".format(dumm, i)
        return dumm

    def remove_tags(self, html):
        # parse html content
        soup = BeautifulSoup(html, "html.parser")
        for data in soup(['style', 'script']):
            # Remove tags
            data.decompose()
        # return data by retrieving the tag content
        return ' '.join(soup.stripped_strings)
