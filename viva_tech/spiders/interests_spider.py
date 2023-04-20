from pathlib import Path

import scrapy
import re
import csv


class InterestSpider(scrapy.Spider):
    name = "Interests"

    def start_requests(self):
        url = "https://vivatechnology.com/the-big-list"
        yield scrapy.Request(url=url, callback=self.parse)

    def file_csv(self, file, array_of_data):
        with open(file, 'w') as f:
            writer = csv.writer(f)
            header = ['name', 'picture', 'place', 'sectors', 'interests']

            writer.writerow(header)
            for item in array_of_data:
                writer.writerow([
                    item['name'].strip('"') if item['name'] else None,
                    item['picture'].strip('"') if item['picture'] else None,
                    item['place'].strip('"') if item['place'] else None,
                    item['sectors'] if item['sectors'] else None,
                    item['interests'] if item['interests'] else None,
                ])

    def parse_cards(self, response_css):
        cardsSet = []
        for item in response_css:
            place = []

            if re.match(r'<div class="card_card_inner__ap7TW"><div class="card_card_inner__ap7TW">', item) is None:
                item = re.sub(r'^<div class="card_card_inner__ap7TW"><div class="card_card-logo__w39sH"><img src=', '', item)
            else:
                item = re.sub(r'<div class="card_card_inner__ap7TW"><div class="card_card_inner__ap7TW"><span>', '', item)
                place = re.sub(r'<$', '', (re.search(r'^\w\d{2}<', item)[0]))

            url = re.search(r'^"https://\S+', item)[0]
            item = re.sub(r'^alt=', '', re.sub(r'^"https://\S+" ', '', item))
            alt = re.search(r'^\"(\W*)*?\w(\W*\w*)*?[()]*?\"[></div><div class=\"card_card-edito__y3oBu\"]', item)[0]

            if re.search(r'^\"(\W*)*?\w(\W*\w*)*?[()]*?\"[></div><div class=\"card_card-edito__y3oBu\"]', alt) is not None:
                alt = re.sub(r'></div><div class=\"card_card-edito__y3oBu\"', '', alt)

            alt = re.sub(r'>$', '', alt)
            item = re.sub(r'^"(\W*)*?\w+(\W*\w*)*?".+</h3><div class="card_sector__G7SSX">', '', item)
            sectors = re.sub(r'<$', '', (re.search(r'^\w+(\W*\w*)*?<', item)[0])).split('/')

            interests = []
            if re.match('^.*(<ul class="card_list__drQwI"><li class="card_element-tags__bGG1y"><span>)', item):
                item = re.sub('^.*(<ul class="card_list__drQwI"><li class="card_element-tags__bGG1y"><span>)', '', item)

                while re.match(r'^\w+(\W*\w*)*?</span></li></ul>(</div>){4}', item) is not None:
                    interests.append(re.sub(r'<', '', (re.search(r'^\w+(\W*\w*)*?<', item)[0])))
                    if re.match(r'^\w+(\W*\w*)*?</span></li></ul>(</div>){4}', item) is not None:
                        break

                    item = re.sub(r'^\w+(\W*\w*)+?</span></li><li class="card_element-tags__bGG1y"><span>', '', item)

            cardsSet.append({
                'name': alt,
                'picture': url,
                'place': place if place else None,
                'sectors': sectors,
                'interests': interests,
            })

        self.file_csv('./data.csv', cardsSet)

    def parse(self, response):
        self.parse_cards(response.css("div.card_card_inner__ap7TW").getall())
