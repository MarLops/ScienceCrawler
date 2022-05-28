from os import stat
from tkinter.messagebox import NO
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

    def check_exist(self,article):
        result = None
        with self.driver.session() as session:
            result = session.write_transaction(self._check_article_exist, article)
        return result

    def create_article(self, article):
        with self.driver.session() as session:
            if session.write_transaction(self._check_article_exist,article['id']) == None:
                greeting = session.write_transaction(self._create_article, article)
                greeting = session.write_transaction(self._create_author, article)


    def change_metadado(self, id_article,metadado,metadado_value):
        with self.driver.session() as session:
            if session.write_transaction(self._check_article_exist,id_article) == None:
                greeting = session.write_transaction(self._change_metadado,id_article,metadado,metadado_value)

        
    def create_connection_ref(self,id_article,article_cited):
        with self.driver.session() as session:
            if session.write_transaction(self._check_article_exist,article_cited['id']) == None:
                self.create_article(article_cited)
            greeting = session.write_transaction(self._check_create_connect, id_article,article_cited['id'])
           
    @staticmethod
    def _create_article(tx, article):
        result = tx.run("MERGE (a:Article {_id: $id,title: $title,doi : $doi,abstract: $abstract, pubmed_url: $url}) RETURN a ",id=article['id'],title=article['title'],doi=article['doi'],abstract=article['abstract'],url=article['pubmed_url'])
        if article['metadado'] is not None:
            metadado = article['metadado']
            try:
                result = tx.run("MATCH (a:Article {_id: $id}) SET a.date = date($date), a.type = $type, a.publisher = $publisher  RETURN a ",id=article['id'],
                                title=article['title'],date=metadado['date'],type=article['type'],publisher=metadado['publisher'])
            except Exception as ex:
                print(ex)
        return result


    @staticmethod
    def _change_metadado(tx, _id,metadado,metadado_value):
        result = tx.run("MATCH (a:Article {_id: $id}) SET a." +metadado + "= $value RETURN a ",id=_id,value=metadado_value)
        return result

    @staticmethod
    def _check_article_exist(tx, id):
        text = 'MATCH (a:Article {_id:"' +  id + '"}) RETURN a._id'
        result = tx.run(text)
        if result.single() is None:
            return None
        try:
            return result.single()[0]
        except:
            return None

    @staticmethod
    def _check_create_connect(tx, id_article,id_article_cited):
        result = tx.run("MATCH (a:Article {_id: $id}), (b:Article {_id: $id_cited}) MERGE (a)-[p:CITED]->(b) RETURN p", 
                        id=id_article,id_cited=id_article_cited)
        return result

    @staticmethod
    def _create_author(tx,article):
        if article['metadado'] is not None:
            if article['metadado']['authors'] is not None:
                for author in article['metadado']['authors']:
                    id_author = author['family'].lower().replace(" ","") + author['given'].lower().replace(" ","")
                    result = tx.run("MERGE (n:Author {id: $id, name: $name})", 
                                id=id_author,name=author['family'] + author['given'])
                    result = tx.run("MATCH (a:Article {_id:$id}), (b:Author {id:$idA}) MERGE (a)-[p:WRITE_BY]-(b) RETURN a,b",id=article['id'],idA=id_author)
            else:
                for author in article['authors']:
                    id_author = author['author'].lower().replace(" ","")
                    result = tx.run("MERGE (n:Author {id: $id, name: $name})", 
                                id=id_author,name=author['author'])
                    result = tx.run("MATCH (a:Article {_id:$id}), (b:Author {id:$idA}) MERGE (a)-[p:WRITE_BY]-(b) RETURN a,b",id=article['id'],idA=id_author)
        else:
            for author in article['authors']:
                id_author = author['author'].lower().replace(" ","")
                result = tx.run("MERGE (n:Author {id: $id, name: $name})", 
                            id=id_author,name=author['author'])
                result = tx.run("MATCH (a:Article {_id:$id}), (b:Author {id:$idA}) MERGE (a)-[p:WRITE_BY]-(b) RETURN a,b",id=article['id'],idA=id_author)
        