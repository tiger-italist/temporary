from elasticsearch_dsl import Index
from model.product import Product
from search.connections import es_connect, db_connect, db_close


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
    product = Product()
    product.product_id = product_id
    product.product_version_id = product_version_id
    product.brand_id = brand_id
    product.brand = brand
    product.category_ids = category_ids
    product.categories = categories
    product.images = '{} {}'.format(image1, image2)
    product.gender = Text()
    product.model = model
    product.model_number_complete = model_number_complete
    product.season = Text()
    product.sizes = Text()
    product.price_eur = rrp_eur_ex_tax
    product.sale_price_eur = Float()
    product.discount_percentage = reduction
    product.description = description
    product.insert_time = pv_insert_time
    product.photo_quality = photo_quality_store
    product.save()


def index_products():
    cnx = db_connect()
    try:
        with cnx.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(product_version_id) FROM mkt_product_search"
                " WHERE lang_id = 2 AND store_is_active = 'Y' AND p_is_active = 'Y'"
                " AND pv_is_active = 'Y' AND is_deleted = 'N';"
            )
            count = cursor.fetchone()[0]
            batch = 1000
            for offset in xrange(0, count, batch):
                cursor.execute(
                    "SELECT p.product_id, p.product_version_id, p.brand_id, p.category_ids, p.model, p.season, p.year,"
                    " p.gender_id, p.categories, p.brand, p.model_number_complete, p.description, p.pv_insert_time,"
                    " p.rrp_eur_ex_tax, p.reduction, p.photo_quality_store, im1.image AS image1, im2.image AS image2,"
                    " GROUP_CONCAT(pvo.size_system_id SEPARATOR ',') AS sizes,"
                    " GROUP_CONCAT(pvo.nr_available SEPARATOR ',') AS quantities"
                    " FROM mkt_product_search p"
                    " JOIN mkt_product_version_option pvo ON p.product_version_id = pvo.product_version_id AND"
                    " pvo.nr_available > 0"
                    " JOIN mkt_product_image im1 ON im1.product_version_id = p.product_version_id AND im1.sort = 1"
                    " JOIN mkt_product_image im2 ON im2.product_version_id = p.product_version_id AND im2.sort = 2"
                    " JOIN store s ON p.store_id = s.store_id AND s.is_active = 'Y'"
                    " WHERE p.p_is_active = 'Y' AND p.pv_is_active = 'Y' AND p.is_deleted = 'N'"
                    " GROUP BY p.product_version_id LIMIT %s OFFSET %s",
                    (batch, offset)
                )
                for row in cursor:
                    index_product(**row)
    finally:
        db_close()
