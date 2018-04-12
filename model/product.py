from elasticsearch_dsl import analyzer, Date, DocType, Float, Integer, Keyword, Text


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
    categories = Text(analyzer=unicode_text)
    images = Keyword(index=False)
    gender = Keyword(multi=True)
    model = Text(analyzer=unicode_text)
    model_number_complete = Text()
    season = Keyword()
    sizes = Keyword(multi=True)
    price_eur = Float()
    sale_price_eur = Float()
    discount_percentage = Integer()
    description = Text(analyzer=html_strip)
    insert_time = Date()
    photo_quality = Integer()

    class Meta:
        index = 'products'
