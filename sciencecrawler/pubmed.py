import datetime
import functools
import re
import time
from typing import List
import requests
from bs4 import BeautifulSoup
from .src.base import SearchBase,ArticleBase





class PubmedArticle(ArticleBase):
    """
    """
    def __init__(self, url):
        page_detail = requests.get(url)
        self._page_soup = BeautifulSoup(page_detail.content, 'html.parser')
        self._infos = self._page_soup.find('div',{"id":"full-view-heading"})
        doi = self.doi.replace("doi: ","").strip()[:-1]
        response = requests.get(f'https://api.crossref.org/works/{doi}')
        if response.status_code < 400:
            self._metadada = response.json()
        else:
            self._metadada = None
        self.url = url


    def publication_type(self):
        try:
            return self._infos.find('div',{"class":"publication-type"}).text
        except:
            return ''


    def journal(self):
       return  self._infos.find('button',{"id":"full-view-journal-trigger"})['title']

    @property
    def doi(self):
        return self._infos.find('span',{"class":"citation-doi"}).text.strip()

    @property
    def title(self):
        return self._infos.find('h1',{"class":"heading-title"}).text.strip()

    @property
    def authors(self):
        spans =  self._infos.find_all('span',{"class":"authors-list-item"})
        response = list()
        for span in spans:
            author = span.find('a',{"class":"full-name"}).text
            indices = span.find_all('a',{"class":"affiliation-link"})
            response.append({"author":author,"index":[int(indice.text) for indice in indices]})
        return response

    @property
    def date(self):
        try:
            return self._infos.find('span',{"class":"secondary-date"}).text.strip()
        except:
            return ''


    def cited_number(self):
        cited =  self._page_soup.find('div',{"id":"citedby"})
        return cited.find('em',{"class":"amount"}).text

    def cited_articles(self):
        try:
            cited =  self._page_soup.find('div',{"id":"citedby"})
            response = list()
            for art in cited.find_all('li',{"class":"full-docsum"}):
                response.append(art.find('a',{"class":"docsum-title"}).text.strip())
            return response
        except:
            return ''


    def affiliation(self):
        div_aff = self._page_soup.find('div',{"id":"full-view-expanded-authors"})
        lis = div_aff.find_all('li')
        response = list()
        for li in lis:
            name = li.text
            key = li.find('sup').text
            response.append({"affiliation":name[2:],"index":int(key)})
        return response

    

    def author_affilition(self):
        authors = self.authors
        affilition = self.affiliation
        response = list()
        for author in authors:
            name_author = author['author']
            indices = author['index']
            affiliton_name = list()
            for indice in indices:
                affiliton_name.append(affilition[indice - 1]["affiliation"])
            response.append({"author":name_author,"affilition":affiliton_name})
        return response


    @property
    def substance(self):
        return self.get_substance()

    def get_substance(self):
        try:
            abstract = self._page_soup.find('div',{"id":"substances"})
            abstract_text = abstract.find_all('button')
            return "<sep>".join([i.text.replace("\n","").strip() for i in abstract_text])
        except:
            return ''

    @property
    def mesh(self):
        return self.get_mesh()

    def get_mesh(self):
        try:
            abstract = self._page_soup.find('div',{"id":"mesh-terms"})
            abstract_text = abstract.find_all('button')
            return "<sep>".join([i.text.replace("\n","").strip() for i in abstract_text])
        except:
            return ''

    def abstract(self):
        try:
            abstract = self._page_soup.find('div',{"id":"abstract"})
            abstract_text = abstract.findAll('div',{"id":"enc-abstract"}).find_all('p')
            return "<sep>".join([i.text.replace("\n","").strip() for i in abstract_text])
        except:
            return ''

    def keywords(self):
        try:
            abstract = self._page_soup.find('div',{"id":"abstract"})
            keywords = abstract.findChildren('p')[-1].text.replace("\n","").strip()
            if "Keywords: " in keywords:
                return keywords
            return ''
        except:
            return ''

    def __repr__(self) -> str:
        return f'Tile: {self.title} | url : {self.url}' 

    def __str__(self):
        return f'Tile: {self.title} | url : {self.url}' 

    def get_references_name(self) -> List[str]:
        try:
            url_reference = self.url + "/references/"
            references = requests.get(url_reference)
            if references.status_code >= 300:
                raise Exception('No references')
            page_soup_references = BeautifulSoup(references.content,'html.parser')
            div_main = page_soup_references.find('div',{"id":"full-references-list"})
            ols = div_main.find('ol',{"id":"full-references-list-1"}).find_all('ol')
            if len(ols) < 1:
                return ''
            return [i.find('li',{'class':"skip-numbering"}).text.replace("\n","").split("  -   ")[0].strip() for i in ols]
        except:
            return ''
        
    
    def get_references(self,interval_requests: int=2) -> List:
        url_reference = self.url + "/references/"
        references = requests.get(url_reference)
        if references.status_code >= 300:
            raise Exception('No references')
        page_soup_references = BeautifulSoup(references.content,'html.parser')
        div_main = page_soup_references.find('div',{"id":"full-references-list"})
        ols = div_main.find('ol',{"id":"full-references-list-1"}).find_all('ol')
        if len(ols) < 1:
            return ''
        response = list()
        print(f'Number references - {len(ols)}')
        for ol in ols:
            try:
                ahrefs = ol.find_all('a',{'class':"reference-link"})
                if len(ahrefs) == 2:
                    href = ahrefs[1]['href']
                else:
                    href = ahrefs[0]['href']
                if "doi" not in  href: 
                    page = PubmedArticle("https://pubmed.ncbi.nlm.nih.gov" + href)
                    response.append(page)
                    time.sleep(interval_requests)
            except:
                pass
        return response


    def conflict_of_interest(self):
        div_conflict = self._page_soup.find('div',{"id":"conflict-of-interest"})
        if div_conflict is None:
            return ''
        return div_conflict.find('p').text

    def to_json(self):
        response = dict()
        response['id'] = self.doi.replace("doi: ","").replace("/","").replace(".","").lower().strip()
        response['pubmed_url'] = self.url
        response['authors'] = self.authors
        response['title'] = self.title
        response['references'] = self.get_references_name()
        response['doi'] = self.doi
        response['journal'] = self.journal()
        response['substances'] = self.get_substance()
        response['mesh'] = self.get_mesh()
        response['type'] = self.publication_type()
        response['date'] = self.date
        response['abstract'] = self.abstract()
        response['conflict'] = self.conflict_of_interest()
        response['cited_articles'] = self.cited_articles()
        response['keywords'] = self.keywords()
        response['pubmed_url'] = self.url
        response['metadado']  = None
        if self._metadada is not None:
            response['metadado'] = dict()
            response['metadado']['funder'] = list()
            if "funder" in self._metadada["message"]:
                response['metadado']['funder'] = self._metadada["message"]["funder"]
            response['metadado']['type'] = self._metadada["message"]["type"]
            response['metadado']['publisher'] = self._metadada["message"]["publisher"]
            response['metadado']['date'] = datetime.datetime.fromtimestamp(int(self._metadada["message"]["created"]["timestamp"]/1000)).strftime("%Y-%m-%d")
            if 'authors' in response['metadado']:
                response['metadado']['authors'] = self._metadada["message"]['author']
            else:
                response['metadado']['authors'] = None
        return response


    def __eq__(self, other):
        return other.title == self.title


    



class PubmedSearch(SearchBase):
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
            try:
                total = self._page_soup.find('div',{"class":"results-amount-container"}).find('span').text
                self.total_search = int(total.replace(",",""))
            except:
                self.total_search = None
        else:
            self._page_soup = None
            self.total_search = None
        

    def get_list_articles(self, interval_requests:int = 2) -> List[PubmedArticle]:
        if self._page_soup is not None:
            articles = self._page_soup.find_all('article',{"class":"full-docsum"})
            links = ["https://pubmed.ncbi.nlm.nih.gov" + article.find('a',{'class':'docsum-title'})['href'] for article in articles]
            response = list()
            for link in links:
                try:
                    response.append(PubmedArticle(link))
                    time.sleep(interval_requests)
                except Exception as ex:
                    continue
            return response
    
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

    def __repr__(self) -> str:
        return f'term: {self._term} / page - {self._page}'

    @property
    def search_term(self):
        return self._term
