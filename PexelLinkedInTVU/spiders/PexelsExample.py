# -*- coding: utf-8 -*-
import scrapy
# Importons le module d'expression régulière
import re
# Puis deux modules d'extraction et de sélection de Scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector


class PexelsexampleSpider(scrapy.Spider):
    name = 'PexelsExample'
    allowed_domains = ['pexels.com']
    start_urls = ['https://pexels.com/']

    # On définit les expression régulières utiles pour filtrer les liens
    url_matcher = re.compile('^https:\/\/www\.pexels\.com\/photo\/')
    src_extractor = re.compile('src="([^"]*)"')
    tags_extractor = re.compile('alt="([^"]*)"')

    # Créons un ensemble pour se souvenir des identifiants déjà visités
    crawled_ids = set()

    def parse(self, response):
        body = Selector(text=response.body)
        # On peut extraire les imes
        images = body.css('img.image-section__image').extract()

        # On récupère les liens des images, et la description
        for image in images:
            img_url = PexelsexampleSpider.src_extractor.findall(image)[0]
            tags = [tag.replace(',', '').lower() for tag in PexelsexampleSpider.tags_extractor.findall(image)[0].split(' ')]
            print(img_url, tags)
            yield {'image_urls': [img_url]}

        # On extrait tous les liens de la page visitée
        link_extractor = LinkExtractor(allow=PexelsexampleSpider.url_matcher)
        # On ne conserve que ceux pas encore visités
        next_links = [link.url for link in link_extractor.extract_links(response) if not self.is_extracted(link.url)]

        # Et on demande à les visiter
        for link in next_links:
            yield scrapy.Request(link, self.parse)

    def is_extracted(self, url):
        # On récupère l'identifiant en fin de lien
        id = int(url.split('/')[-2].split('-')[-1])
        if id not in PexelsexampleSpider.crawled_ids:
            PexelsexampleSpider.crawled_ids.add(id)
            # On retourne faux si nous n'avons jamais visité cette page
            return False
        return True