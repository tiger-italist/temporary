from elasticsearch_dsl import DocType, analyzer, Text, Integer, Float, Date


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class Product(DocType):
    product_version_id = Integer()
    product_id = Integer()
    brand_id = Integer()
    brand = Text()
    category_ids = Integer(multi=True)
    categories = Text()
    images = Text(index=False)
    gender = Text()
    model = Text()
    model_number_complete = Text()
    season = Text()
    price_eur = Float()
    sale_price_eur = Float()
    discount_percentage = Integer()
    description = Text(analyzer=html_strip)
    insert_time = Date()
    photo_quality = Integer()

    class Meta:
        index = 'products'
