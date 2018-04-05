from re import split
from elasticsearch_dsl import Index
from model.product import Product
from connections import es_connect, db_connect, db_close


def _format_season(season, year):
    formatted_season = 'SS' if season == 'P/E' else 'FW' if season == 'A/I' else None
    formatted_year = split('\\D', year.strip())[0][-2:]
    if formatted_season and formatted_year:
        return '{}{}'.format(formatted_season, formatted_year)
    else:
        return 'Classic'


def _format_gender(gender_id):
    return 'M' if gender_id == 1 else 'F' if gender_id == 2 else 'M F'


def _format_sizes(sizes, quantities):
    inventory = zip(sizes.split(','), quantities.split(','))
    return list(set(map(lambda x: x[0], filter(lambda x: int(x[1]) > 0, inventory))))


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


def index_product(
    product_id, product_version_id, brand_id, brand, category_ids, categories, gender_id, model_number_complete,
    model, season, year, description, pv_insert_time, rrp_eur_ex_tax, reduction, photo_quality_store, image1,
    image2, sizes, quantities
):
    try:
        product = Product()
        product.product_id = product_id
        product.product_version_id = product_version_id
        product.brand_id = brand_id
        product.brand = brand
        product.category_ids = map(lambda x: int(x), category_ids.split(','))
        product.categories = categories.split(',')
        product.images = '{} {}'.format(image1, image2)
        product.gender = _format_gender(gender_id)
        product.model = model
        product.model_number_complete = model_number_complete
        product.season = _format_season(season, year)
        product.sizes = _format_sizes(sizes, quantities)
        product.price_eur = round(float(rrp_eur_ex_tax), 2)
        product.sale_price_eur = (
            round(float(rrp_eur_ex_tax) * (100 - reduction) / 100.0, 2) if reduction
            else round(float(rrp_eur_ex_tax), 2)
        )
        product.discount_percentage = reduction
        product.description = description
        product.insert_time = pv_insert_time
        product.photo_quality = photo_quality_store
        product.save()
    except:
        print 'product {} discarded due to exception'.format(product_version_id)


def index_products(batchsize=1000):
    es_connect()
    cnx = db_connect()
    try:
        with cnx.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(product_version_id) FROM mkt_product_search"
                " WHERE lang_id = 2 AND store_is_active = 'Y' AND p_is_active = 'Y'"
                " AND pv_is_active = 'Y' AND is_deleted = 'N';"
            )
            count = cursor.fetchone()[0]
            product_fields = (
                'product_id', 'product_version_id', 'brand_id', 'category_ids', 'model', 'season', 'year', 'gender_id',
                'categories', 'brand', 'model_number_complete', 'description', 'pv_insert_time', 'rrp_eur_ex_tax',
                'reduction', 'photo_quality_store', 'image1', 'image2', 'sizes', 'quantities'
            )
            for offset in xrange(0, count, batchsize):
                cursor.execute(
                    "SELECT p.product_id, p.product_version_id, p.brand_id, p.category_ids, p.model, p.season, p.year,"
                    " p.gender_id, p.categories, p.brand, p.model_number_complete, p.description, p.pv_insert_time,"
                    " p.rrp_eur_ex_tax, p.reduction, p.photo_quality_store, im1.image AS image1, im2.image AS image2,"
                    " GROUP_CONCAT(su2.value SEPARATOR ',') AS sizes,"
                    " GROUP_CONCAT(pvo.nr_available SEPARATOR ',') AS quantities"
                    " FROM mkt_product_search p"
                    " JOIN mkt_product_version_option pvo ON p.product_version_id = pvo.product_version_id AND"
                    " pvo.nr_available > 0"
                    " JOIN mkt_product_image im1 ON im1.product_version_id = p.product_version_id AND im1.sort = 1"
                    " JOIN mkt_product_image im2 ON im2.product_version_id = p.product_version_id AND im2.sort = 2"
                    " JOIN store s ON p.store_id = s.store_id AND s.is_active = 'Y'"
                    " JOIN mkt_size_unit_system su1 ON pvo.size_system_id = su1.size_system_id"
                    " JOIN mkt_size_unit_system su2 ON su1.size_id = su2.size_id AND su2.unit_system_id = 1"
                    " WHERE p.lang_id = 2 AND p.p_is_active = 'Y' AND p.pv_is_active = 'Y' AND p.is_deleted = 'N'"
                    " GROUP BY p.product_version_id LIMIT %s OFFSET %s",
                    (batchsize, offset)
                )
                for row in cursor:
                    index_product(**dict(zip(product_fields, row)))
    finally:
        db_close()


if __name__ == '__main__':
    create_product_index()
    index_products(1000)
