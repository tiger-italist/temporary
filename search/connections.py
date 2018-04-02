from elasticsearch_dsl.connections import connections


def connect():
    connections.create_connection(
        hosts=['localhost'],
    )
