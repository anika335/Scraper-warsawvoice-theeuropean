#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import date


# Article Klasse die die zu scrapenden Daten speichert
class Article:
    def __init__(self, headline, link, text_body, source, source_name, author, topic, crawl_date, creation_date):
        self.headline = headline
        self.link = link
        self.text_body = text_body
        self.source = source
        self.sourceName = source_name
        self.author = author
        self.topic = topic
        self.crawl_date = crawl_date
        self.creation_date = creation_date

    # Helfer Methode die es später ermöglicht einen JSON String zu erstellen
    # siehe return von 'def get_articles()'
    def serialize(self):
        return {
            'headline': self.headline,
            'textBody': self.text_body,
            'source': self.source,
            'sourceName': self.sourceName,
            'author': self.author,
            'topic': self.topic,
            'link': self.link,
            'crawlDate': self.crawl_date,
            'creationDate': self.creation_date,
        }


# Sucht sich die eine Liste mit allen Artikel links zusammen
# Für theeuropean.de
def get_news_links_de(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    item = soup.find_all('div', class_='news_box_item')

    links = []
    for item in item:
        if item.find('a'):
            links.append(item.find('a').get('href').strip())
    return links


# Extrahiert alle notwendigen informationen von einem einzigen Artikel
# Für theeuropean.de

def scrape_de(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    [s.extract() for s in soup('script')]  # entfernt alle script tags
    # HEADLINE
    headline = soup.find('h1', class_='entry-title title post_title').string

    # TOPIC
    topic = soup.find('span', class_='article_dots cat').string

    # AUTHOR
    author = soup.find('div', class_='von').contents[2][1:]

    # TEXT_BODY
    text_body = soup.find('div', 'post_content_inner_wrapper content_inner_wrapper entry-content').get_text()

    # CREATION_DATE
    creation_date = soup.find('div', class_='von').find('span', class_='article_dots').string

    return Article(headline, link, text_body, 'https://www.theeuropean.de', 'theeuropean', author, topic, date.today(), creation_date)

# Für warsawvoice.pl
def get_news_links_pl(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    item = soup.find_all('div', class_='artTitle')
    item2 = soup.find_all('div', class_='newsTitle')
    item3 = soup.find_all('div', class_='newsTitleS')

    links = []
    for item in item:
        if item.find('a'):
            links.append(item.find('a').get('href').strip())

    for item in item2:
        if item.find('a'):
            links.append(item.find('a').get('href').strip())

    for item in item3:
        if item.find('a'):
            links.append(item.find('a').get('href').strip())
    return links

# Für tygodnikpowszechny.pl
def scrape_pl(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    [s.extract() for s in soup('script')]  # entfernt alle script tags

    # HEADLINE
    headline = ''
    hl = soup.find('div', class_='artTitle')
    if hl is not None:
        headline = hl.string

    # TOPIC
    topic = ''
    # AUTHOR
    author = ''

    # TEXT_BODY
    text_body = ''
    tb = soup.find('div', class_='artFull')
    for div in tb.find_all('div'):
        div.clear()

    text_body = tb.get_text()

    # CREATION_DATE
    creation_date = ''
    d = soup.find('div', class_='artDate')
    if d is not None:
        creationDate = d.string

    return Article(headline, link, text_body, 'http://www.warsawvoice.pl', 'warsawvoice', author, topic, date.today(), creation_date)

# ************************* Flask web app *************************  #


app = Flask(__name__)

# Hier wird der Pfad(route) angegeben der den scraper arbeiten lässt.
# In dem Fall ist die URL "localhost:5000/theeuropean"
@app.route('/theeuropean')
def get_articles():
    links = get_news_links_de('https://www.theeuropean.de')
    articles = []
    for link in links:
        articles.append(scrape_de(link))
    return jsonify([e.serialize() for e in articles])  # jsonify erzeugt aus einem Objekt einen String im JSON Format

@app.route('/warsawvoice')
def get_articles_pol():
    links = get_news_links_pl('http://www.warsawvoice.pl')
    articles = []
    for link in links:
        articles.append(scrape_pl(link))
    return jsonify([e.serialize() for e in articles])  # jsonify erzeugt aus einem Objekt einen String im JSON Format

@app.route('/')
def index():
    return "<h1>Hier passiert nichts. Bitte gehe zu '/theeuropean oder /warsawvoice</h1>"


# Web Application wird gestartet
if __name__ == '__main__':
    app.run()
