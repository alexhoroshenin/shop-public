from .json_converter import CategoryParserModel, ProductParserModel, BalanceParserModel, parse_json


class JsonConverter:

    def __init__(self, input_json):
        self.input_json = input_json
        self.products = None
        self.categories = None
        self.offers = None

    def parse_json(self):
        products = self.input_json.get('products')
        categories = self.input_json.get('categories')
        offers = self.input_json.get('offers')
        if products:
            self.products = parse_json(ProductParserModel, products)

        if categories:
            self.categories = parse_json(CategoryParserModel, categories)

        if offers:
            self.categories = parse_json(BalanceParserModel, offers)

    def __int__(self):
        return f"JsonConverter: products: {len(self.products)}, " \
               f"categories: {len(self.categories)}, " \
               f"offers: : {len(self.offers)}"
