from elasticsearch_dsl import DocType, analyzer, Text, Integer, Float, Date


html_strip = analyzer(
    'html_strip',
    tokenizer="icu_tokenizer",
    filter=["standard", "icu_normalizer", "stop", "snowball"],
    char_filter=["html_strip"]
)


unicode_text = analyzer(
    'unicode_text',
    tokenizer='icu_tokenizer',
    filter=["standard", "icu_normalizer"]
)


class Product(DocType):
    product_id = Integer()
    product_version_id = Integer()
    brand_id = Integer()
    brand = Text(analyzer=unicode_text)
    category_ids = Integer(multi=True)
    categories = Text()
    images = Text(index=False)
    gender = Text()
    model = Text(analyzer=unicode_text)
    model_number_complete = Text()
    season = Text()
    sizes = Text()
    price_eur = Float()
    sale_price_eur = Float()
    discount_percentage = Integer()
    description = Text(analyzer=html_strip)
    insert_time = Date()
    photo_quality = Integer()

    class Meta:
        index = 'products'
