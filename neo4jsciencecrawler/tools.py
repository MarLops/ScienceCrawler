def check_article(article,words):
    for word in words:
        if word.lower() in article['title'].lower():
            return True
        if word.lower() in article['abstract'].lower():
            return True
        if word.lower() in article['substances'].lower():
            return True
        if word.lower() in article['mesh'].lower():
            return True
    return False