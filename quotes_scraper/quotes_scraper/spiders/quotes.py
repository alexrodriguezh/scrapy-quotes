import scrapy

# Título = //h1/a/text()
# Citas = //span[@class="text" and @itemprop="text"]/text()
# Top ten tags = //div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()
# Next page button = //ul[@class="pager"]//li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1'
    ]
    custom_settings = {
        'FEED_URI' : 'quotes.json',
        'FEED_FORMAT' : 'json',
        'FEED_EXPORT_ENCODING': 'utf-8', # Nos ayuda a diferenciar tildes y ñ
        'CONCURRENT_REQUEST': 24, # Con esto le decimos que haga 24 peticiones a la vez
        'MEMUSAGE_LIMIT_MB': 2048, # Aquí le indicamos cuanta memoria RAM usar al framework
        'MEMUSAGE_NOTIFY_MAIL': ['arodriguez2407@gmail.com'], # Si mi memoria RAM llega a ser superada que me avise a este correo
        'ROBOTSTXT_OBEY': True, # Le decimos que haga caso a robots.txt
        'USER_AGENT': 'Scraper' # El nombre que queremos que aparezca al hacer scraping
    }

    def parse_only_quotes(self, response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
            authors = kwargs['authors']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())
        authors.extend(response.xpath('//small[@class="author" and @itemprop="author"]/text()').getall())

        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes': quotes, 'authors': authors})
        else:
            yield {
				'quotes':  list(zip(quotes, authors))
			}

    def parse(self, response):

        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        authors = response.xpath('//small[@class="author" and @itemprop="author"]/text()').getall()
        top_tags = response.xpath('//div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()').getall()

        # Este es una función que viene en el core de python
        # Con esto llamaremos a scrapy crawl quotes -a top=5
        # Y nos devolverá solo el top 5
        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield {
            'title': title,
            'top_tags':top_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes': quotes, 'authors': authors})
