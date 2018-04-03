from elasticsearch_dsl import Index
from model.product import Product
from search.connections import es_connect, db_connect


def create_product_index():
    es_connect()
    products = Index('products')
    products.settings(
        number_of_shards=1,
        number_of_replicas=0
    )
    products.doc_type(Product)
    products.delete(ignore=404)
    products.create()


def index_product():
    pass


def index_products():
    cnx = db_connect()
