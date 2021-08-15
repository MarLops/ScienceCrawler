import functools
import time
from typing import List
import requests
from bs4 import BeautifulSoup
from .src.base import SearchBase,ArticleBase


class GoogleSearch(SearchBase):
    def __init__(self, term, cites = None, language = 'en-us'):
        params = dict()
        self._term = term
        self._cites = cites
        self._page = 1
        params = dict()
        self._start = 0
        self._language = language
        if term is not None:
            params['q'] = term
            params['hl'] = language
        else:
            if cites is not None:
                params['cites'] = cites
        response = requests.get('https://scholar.google.com/scholar',params=params)
        self.reponse_status = response.status_code
        if response.status_code < 300:
            self._page_soup = BeautifulSoup(response.content, 'html.parser')
        else:
            self._page_soup = None

    
    @property
    def current_page(self):
        return self._page


    def __repr__(self) -> str:
        if self._term is not None:
            return f'term: {self._term} / page: {self._page}'
        else:
            return f'cites: {self._cites} / page: {self._page}'


    def get_list_articles(self, interval_requests:int = 0.5):
        if self._page_soup is not None:
            div_main = self._page_soup.find('div',{"id":"gs_res_ccl_mid"})
            articles = div_main.find_all('div',{"class":"gs_ri"})
            response = list()
            for article in articles:
                try:
                    article_response = dict()
                    
                    a_article = article.find("h3",{"class":"gs_rt"}).find('a')
                    link = a_article['href']
                    article_response['link'] = link
                    title = a_article.text
                    article_response['title'] = title

                    author = article.find('div',{"gs_a"}).text
                    article_response['author'] = author
                    resume = article.find('div',{"gs_rs"}).text
                    article_response['resume'] = resume
                    links = article.find('div',{"class":"gs_fl"}).find_all('a')
                    for link in links:
                        try:
                            if  "cites" in link['href']:
                                cited = link['href'].split('&')[0].split('cites=')[-1]
                                article_response['cited'] = GoogleSearch(None,cited)
                            if "scholar.googleuser" in link['href']:
                                link_cache = link['href']
                                article_response['link_html'] = str(requests.get(link_cache).content)
                        except Exception as ex: 
                            print(ex)
                    time.sleep(interval_requests)
                    response.append(article_response)
                except:
                    pass
            return response

    @property
    def total_search(self):
        try:
            return self._page_soup.find("div",{"id":"gs_ab_md"}).find('div').text
        except:
            return None

    @property
    def search_term(self):
        return self._term
          
    def get_next_page(self):
        self._start = self._start + 10
        self._page = self._page + 1
        params = dict()
        if self._term is not None:
            params['q'] = self._term
            params['hl'] = self._language
            params['start'] = self._start
        else:
            if self._cites is not None:
                params['cites'] = self._cites
        response = requests.get('https://scholar.google.com/scholar',params=params)
        self.reponse_status = response.status_code
        if response.status_code < 300:
            self._page_soup = BeautifulSoup(response.content, 'html.parser')
        else:
            self._page_soup = None


    def go_to_page(self,page: int):
        self._start = 10*(page - 1)
        self._page = page
        params = dict()
        if self._term is not None:
            params['q'] = self._term
            params['hl'] = self._language
            params['start'] = self._start
        else:
            if self._cites is not None:
                params['cites'] = self._cites
        response = requests.get('https://scholar.google.com/scholar',params=params)
        self.reponse_status = response.status_code
        if response.status_code < 300:
            self._page_soup = BeautifulSoup(response.content, 'html.parser')
        else:
            self._page_soup = None