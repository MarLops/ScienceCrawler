from sciencecrawler.pubmed import PubmedArticle, PubmedSearch


def test_search_covid():
    search_page = PubmedSearch("COVID 19")
    assert search_page.current_page == 1
    assert search_page.total_search > 160000
    articles_page_one = search_page.get_list_articles()
    search_page.get_next_page()
    articles_page_two = search_page.get_list_articles()
    assert articles_page_one[0] != articles_page_two[0]
    assert articles_page_one != articles_page_two



def test_page_article_33007039():
    article = PubmedArticle('https://pubmed.ncbi.nlm.nih.gov/33007039/')
    assert article.title == 'Brief Report: Hydroxychloroquine does not induce hemolytic anemia or organ damage in a "humanized" G6PD A- mouse model'
    assert "Hydroxychloroquine (HCQ) is widely used in the treatment of malaria," in article.abstract
    assert "I have read the journal's policy and the authors of this manuscript have the following competi" in article.conflict_of_interest
    assert len(article.get_references_name()) == 11
    assert 'Luzzatto L, Nannelli C' in article.get_references_name()[0]