from elasticsearch_dsl.connections import connections
import pymysql


es, db = None, None


def es_connect():
    global es
    if es:
        return es

    connections.create_connection(
        hosts=['localhost'],
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
        db='italist'
    )
    return db
