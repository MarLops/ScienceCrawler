from abc import ABC, abstractmethod, abstractproperty
import keyword
from typing import List
from pydantic import BaseModel


class SearchBase(ABC):
    @abstractmethod
    def get_list_articles(self,interval_requests: int):
        pass

    @abstractmethod
    def get_next_page(self):
        pass

    @abstractmethod
    def go_to_page(self):
        pass

    @property
    @abstractproperty
    def search_term(self):
        pass

    @property
    @abstractproperty
    def current_page(self):
        pass


class ArticleBase(ABC):

    @property
    @abstractproperty
    def doi(self):
        pass

    @property
    @abstractproperty
    def title(self):
        pass

    @property
    @abstractproperty
    def authors(self):
        pass

    @abstractmethod
    def get_references(self):
        pass

    @abstractmethod
    def to_json(self):
        pass




class ArticleOutput(BaseModel):
    id : str
    url: str   
    authors : List[str]
    title : str
    doi : str
    abstract : str
    references : List[str]
    date : str
    type_article : str
    journal : str
    keywords : List[str]
    funder : List[str]

class ArticleCovidHidro(ArticleOutput):
    is_covid : bool
    is_hidro : bool