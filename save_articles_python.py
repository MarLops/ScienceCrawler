# %%
from sciencecrawler.pubmed import PubmedSearch
import json
from neo4jsciencecrawler import Neo4jScienceCrawler
import time

# %%
searchengine = PubmedSearch('covid chloroquine')

# %%
total = searchengine.total_search

# %%
total

# %%
articles_current_page = searchengine.get_list_articles()

# %%
articles_read = len(articles_current_page)

# %%
neo4jC = Neo4jScienceCrawler("bolt://localhost:7687",'neo4j','admin')

# %%
for article in articles_current_page:
    article_json = article.to_json()
    article_json['id'] = article_json['doi'].replace("doi:","").replace("/","").replace(".","").lower().strip()
    neo4jC.create_article(article_json)

# %%
while articles_read < total:
    time.sleep(5)
    print(articles_read)
    searchengine.get_next_page()
    articles_current_page = searchengine.get_list_articles()
    articles_read = articles_read + len(articles_current_page)
    for article in articles_current_page:
        try:
            article_json = article.to_json()
            article_json['id'] = article_json['doi'].replace("doi:","").replace("/","").replace(".","").lower()
            neo4jC.create_article(article_json)
        except Exception as ex:
            print("=======================")
            print(article.title)
            print("\n")
            print(ex)
            print("====================================")

# %%



