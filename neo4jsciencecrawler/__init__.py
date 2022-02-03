from os import stat
from neo4j import GraphDatabase

class Neo4jScienceCrawler:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def configuration_node(self):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._configuration_node)


    @staticmethod
    def _configuration_node(tx):
        result = tx.run("CREATE CONSTRAINT constraint_article_id ON (n:Article) ASSERT n._id IS UNIQUE")
        result = tx.run("CREATE CONSTRAINT constraint_article_name ON (n:Article) ASSERT n.title IS UNIQUE")
        return result

    def create_article(self, article):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._create_article, article)
            greeting = session.write_transaction(self._create_author, article)
            
    @staticmethod
    def _create_article(tx, article):
        result = tx.run("MERGE (a:Article {_id: $id,title: $title,doi : $doi,abstract: $abstract }) RETURN a ",id=article['id'],title=article['title'],doi=article['doi'],abstract=article['abstract'])
        return result

    @staticmethod
    def _check_article_exist(tx, article):
        result = tx.run("MATCH (a:Article {id: '$id'}) RETURN a ", 
                        id=article['id'])
        return result


    @staticmethod
    def _check_create_connect(tx, article,article_cited):
        result = tx.run("MATCH (a:Article {id: $id}) (b:Article {id : $id_cited} MERGE (a)-[p:CITED]->(b) RETURN p", 
                        id=article['id'],id_cited=article_cited['id'])
        return result

    @staticmethod
    def _create_author(tx,article):
        for author in article['authors']:
            id_author = author['author'].lower().replace(" ","")
            result = tx.run("MERGE (n:Author {id: $id, name: $name})", 
                        id=id_author,name=author['author'])
            result = tx.run("MATCH (a:Article {_id:$id}), (b:Author {id:$idA}) MERGE (a)-[p:WRITE_BY]-(b) RETURN a,b",id=article['id'],idA=id_author)
        