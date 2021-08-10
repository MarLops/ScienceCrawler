# ScienceCrawler
Crawler sites as Pubmed, GoogleScholar


## Pubmed

#### Search by term

```python
from sciencecrawler.pubmed import PubmedSearch
search_page = PubmedSearch("Covid")

#get current page
search_page.current_page

# get list of articles from current page
articles_page_one = search_page.get_list_articles()

# get to next page
search_page.get_next_page()

#get list of artciles from page two
articles_page_two = search_page.get_list_articles()

#go to page 5
search_page.go_to_page(5)
```


#### Get article'information

```python
from sciencecrawler.pubmed import PubmedSearch
search_page = PubmedSearch("Covid")
article_one =  search_page.get_list_articles()[0]

#title
print(article_one.title)

#authors
print(article.authors)

#abstract
print(article.abstract)


# get all references articles
refe = article.get_references()


#get all information as json
information = article.to_json()
```


