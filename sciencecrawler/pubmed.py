import functools
import time
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
            try:
                total = self._page_soup.find('div',{"class":"results-amount-container"}).find('span').text
                self.total_search = int(total.replace(",",""))
            except:
                self.total_search = None
        else:
            self._page_soup = None
            self.total_search = None
        

    def get_list_articles(self, interval_requests:int = 2):
        if self._page_soup is not None:
            articles = self._page_soup.find_all('article',{"class":"full-docsum"})
            links = ["https://pubmed.ncbi.nlm.nih.gov" + article.find('a',{'class':'docsum-title'})['href'] for article in articles]
            response = list()
            for link in links:
                response.append(PubmedArticle(link))
                time.sleep(interval_requests)
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
        spans =  self._infos.find_all('span',{"class":"authors-list-item"})
        response = list()
        for span in spans:
            author = span.find('a',{"class":"full-name"}).text
            indices = span.find_all('a',{"class":"affiliation-link"})
            response.append({"author":author,"indices":[int(indice.text) for indice in indices]})
        return response

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

    @functools.cached_property
    def affiliation(self):
        div_aff = self._page_soup.find('div',{"id":"full-view-expanded-authors"})
        lis = div_aff.find_all('li')
        response = list()
        for li in lis:
            name = li.text
            key = li.find('sup').text
            response.append({"affiliation":name,"indice":int(key)})
        return response

    
    @functools.cached_property
    def author_affilition(self):
        authors = self.authors
        affilition = self.affiliation
        response = list()
        for author in authors:
            name_author = author['author']
            indices = author['indices']
            affiliton_name = list()
            for indice in indices:
                affiliton_name.append(affilition[indice]["affiliation"])
            response.append({"author":name_author,"affilition":affiliton_name})
        return response



    @functools.cached_property
    def abstract(self):
        try:
            abstract = self._page_soup.find('div',{"id":"abstract"})
            abstract_text = abstract.find('div',{"id":"enc-abstract"}).find_all('p')
            return [i.text.replace("\n","").strip() for i in abstract_text]
        except:
            raise ValueError("No abstract")

    @functools.cached_property
    def keywords(self):
        try:
            abstract = self._page_soup.find('div',{"id":"abstract"})
            keywords = abstract.findChildren('p').text
            return keywords
        except:
            raise ValueError('No keywords')

    def __repr__(self) -> str:
        return f'Tile: {self.title} | url : {self.url}' 

    def __str__(self):
        return f'Tile: {self.title} | url : {self.url}' 

    def get_references_name(self):
        url_reference = self.url + "/references/"
        references = requests.get(url_reference)
        if references.status_code >= 300:
            raise Exception('No references')
        page_soup_references = BeautifulSoup(references.content,'html.parser')
        div_main = page_soup_references.find('div',{"id":"full-references-list"})
        ols = div_main.find('ol',{"id":"full-references-list-1"}).find_all('ol')
        if len(ols) < 1:
            return None
        return [i.find('li',{'class':"skip-numbering"}).text.replace("\n","").split("  -   ")[0].strip() for i in ols]
        
    
    def get_references(self,interval_requests: int=2):
        url_reference = self.url + "/references/"
        references = requests.get(url_reference)
        if references.status_code >= 300:
            raise Exception('No references')
        page_soup_references = BeautifulSoup(references.content,'html.parser')
        div_main = page_soup_references.find('div',{"id":"full-references-list"})
        ols = div_main.find('ol',{"id":"full-references-list-1"}).find_all('ol')
        if len(ols) < 1:
            return None
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
                    print("https://pubmed.ncbi.nlm.nih.gov" + href)
                    page = PubmedArticle("https://pubmed.ncbi.nlm.nih.gov" + href)
                    response.append(page)
                    time.sleep(interval_requests)
            except:
                pass
        return response


    

