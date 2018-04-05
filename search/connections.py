from elasticsearch_dsl.connections import connections
import pymysql
import certifi


es, db = None, None


def es_connect():
    global es
    if es:
        return es

    connections.create_connection(
        hosts=['https://search-products-test-c3og36q3enkihz6fyh3afrkbwu.us-west-2.es.amazonaws.com'],
        port=443,
        use_ssl=True
    )
    es = connections
    return es


def db_connect():
    global db
    if db:
        return db
    db = pymysql.connect(
        host='52.40.186.85',
        port=1433,
        user='ovojo',
        password='pMubciyfaFH7d3',
        db='italist',
        charset='utf8'
    )
    return db


def db_close():
    global db
    if db:
        db.close()
        db = None
