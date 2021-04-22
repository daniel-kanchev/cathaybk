import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cathaybk.items import Article


class cathaybkSpider(scrapy.Spider):
    name = 'cathaybk'
    start_urls = ['https://www.cathaybk.com.tw/cathaybk/personal/news/announcement/']

    def parse(self, response):
        articles = response.xpath('//ul[@class="news-list"]/li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./a/span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="banner-title"]//span/text()').get() or \
                response.xpath('//div[@class="banner-title"]/text()').get()
        if title:
            title = title.strip()
        else:
            return

        content = response.xpath('//div[@class="paragraph"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
