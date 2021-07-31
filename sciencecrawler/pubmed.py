import functools
import requests
from bs4 import BeautifulSoup

class PubmedSearch:
    """
    """
    def __init__(self, term):
        params = dict()
        self._term = term
        self._page = 1
        params = dict()
        params['term'] = term
        params['page'] = 1
        response = requests.get('https://pubmed.ncbi.nlm.nih.gov/',params=params)
        self.reponse_status = response.status_code
        if response.status_code < 300:
            self._page_soup = BeautifulSoup(response.content, 'html.parser')
        else:
            self._page_soup = None

    def get_list_articles(self):
        if self._page_soup is not None:
            articles = self._page_soup.find_all('article',{"class":"full-docsum"})
            links = ["https://pubmed.ncbi.nlm.nih.gov" + article.find('a',{'class':'docsum-title'})['href'] for article in articles]
            return [PubmedArticle(link) for link in links]
    
    def get_next_page(self):
        self._page =self._page + 1
        params = dict()
        params['term'] = self._term
        params['page'] = self._page
        response = requests.get('https://pubmed.ncbi.nlm.nih.gov/',params=params)
        self.reponse_status = response.status_code
        if response.status_code < 300:
            self._page_soup = BeautifulSoup(response.content, 'html.parser')
        else:
            self._page_soup = None

    @property
    def current_page(self):
        return self._page

    def go_to_page(self,page: int):
        if page < 1:
            raise ValueError('page isn ok')
        self._page = page
        params = dict()
        params['term'] = self._term
        params['page'] = self._page
        response = requests.get('https://pubmed.ncbi.nlm.nih.gov/',params=params)
        self.reponse_status = response.status_code
        if response.status_code < 300:
            self._page_soup = BeautifulSoup(response.content, 'html.parser')
        else:
            self._page_soup = None


class PubmedArticle:
    """
    """
    def __init__(self, url):
        page_detail = requests.get(url)
        self._page_soup = BeautifulSoup(page_detail.content, 'html.parser')
        self._infos = self._page_soup.find('div',{"id":"full-view-heading"})
        self.url = url

    @functools.cached_property
    def publication_type(self):
        return self._infos.find('div',{"class":"publication-type"}).text

    @functools.cached_property
    def journal(self):
       return  self._infos.find('button',{"id":"full-view-journal-trigger"})['title']

    @functools.cached_property
    def doi(self):
        return self._infos.find('span',{"class":"citation-doi"}).text.strip()

    @property
    def title(self):
        return self._infos.find('h1',{"class":"heading-title"}).text.strip()

    @functools.cached_property
    def authors(self):
        return [author.find('a',{"class":"full-name"}).text for author in self._infos.find_all('span',{"class":"authors-list-item"})]

    @property
    def date(self):
        return self._infos.find('span',{"class":"secondary-date"}).text.strip()

    @functools.cached_property
    def cited_number(self):
        cited =  self._page_soup.find('div',{"id":"citedby"})
        return cited.find('em',{"class":"amount"}).text

    @functools.cached_property
    def cited_articles(self):
        cited =  self._page_soup.find('div',{"id":"citedby"})
        response = list()
        for art in cited.find_all('li',{"class":"full-docsum"}):
            response.append(art.find('a',{"class":"docsum-title"}).text.strip())
        return response

    

