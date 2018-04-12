from elasticsearch_dsl import Search


def search_product(
    genders=None, category_ids=None, brand_ids=None, seasons=None, sizes=None, sortby='relevance', onsale=False,
    freetext=None, offset=0, limit=60
):
    filters = []
    if category_ids is not None and len(category_ids) > 0:
        filters.append({'terms': {'category_ids': category_ids}})
    if brand_ids is not None and len(brand_ids) > 0:
        filters.append({'terms': {'brand_id': brand_ids}})
    if genders is not None and len(genders) > 0:
        filters.append({'terms': {'gender': genders}})
    if seasons is not None and len(seasons) > 0:
        filters.append({'terms': {'season': seasons}})
    if sizes is not None and len(sizes) > 0:
        filters.append({'terms': {'sizes': sizes}})
    if onsale:
        filters.append({'range': {'discount_percentage': {'gt': 0}}})

    matches = []
    if freetext:
        matches.append({'match': {'model': {'query': freetext, 'boost': 2.0}}})
        matches.append({'match': {'brand': {'query': freetext, 'boost': 2.0}}})
        matches.append({'match': {'categories': freetext}})
        matches.append({'match': {'description': freetext}})

    sorts = []
    if sortby == 'price_high':
        sorts.append({'price_eur': {'order': 'desc'}})
    elif sortby == 'price_low':
        sorts.append({'price_eur': {'order': 'asc'}})
    elif sortby == 'sale':
        sorts.append({'discount_percentage': {'order': 'desc'}})
    elif sortby == 'newest':
        sorts.append({'insert_time': {'order': 'desc'}})
    sorts.append({'photo_quality': {'order': 'desc'}})
    sorts.append('_score')

    bool_query = {
        'filter': filters
    }
    if len(matches) > 0:
        bool_query['should'] = matches
        bool_query['minimum_should_match'] = 1

    query = {
        'query': {'bool': bool_query},
        'sort': sorts
    }
    print query
    s = Search.from_dict(query)
    for hit in s[offset:offset + limit].execute():
        print hit


if __name__ == '__main__':
    from connections import es_connect
    es_connect()
    search_product(['F'], [108], [481], ['FW17'], ['M'], onsale=False, freetext='Gazelle')
