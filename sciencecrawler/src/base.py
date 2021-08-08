from abc import ABC, abstractmethod, abstractproperty


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

