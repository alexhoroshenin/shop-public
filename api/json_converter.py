from pydantic import BaseModel, ValidationError, Field, parse_obj_as
from typing import List, Optional, Union
from datetime import datetime


class AbstractParserModel(BaseModel):
    @classmethod
    def parse_json(cls, input_json):
        return parse_obj_as(List[cls], input_json)


class CategoryParserModel(AbstractParserModel):
    id_1c: str = Field(None, alias='category_id_1c')
    name: str
    description: Optional[str]
    slug: Optional[str]
    parent_id_1c: Optional[str]


class ProductParserModel(AbstractParserModel):
    id_1c: str = Field(None, alias='product_id_1c')
    name: str
    description: Optional[str]
    model: Optional[str]
    slug: Optional[str]
    group_id_1c: Optional[str]
    vat: Optional[str]
    images: Optional[Union[List[str], str]]
    price: Optional[float]
    discount_percent: Optional[float] = 0
    discount_finish_date: Optional[datetime] = None
    category_id_1c: str = Field(None, alias='group_id_1c')


class BalanceParserModel(AbstractParserModel):
    product_id_1c: str
    price: float
    quantity: float
    currency: Optional[str]
    price_type_id: Optional[str]
    price_type_name: Optional[str]
    warehouse_id_1c: Optional[str]
    warehouse_name: Optional[str]


class JsonConverter:

    def __init__(self, input_json):
        self.input_json = input_json
        self.product = None
        self.category = None
        self.offer = None

        self.parse_json()

    def parse_json(self):
        products = self.input_json.get('products')
        categories = self.input_json.get('categories')
        offers = self.input_json.get('offers')
        if products:
            self.product = ProductParserModel.parse_json(products)

        if categories:
            self.category = CategoryParserModel.parse_json(categories)

        if offers:
            self.category = BalanceParserModel.parse_json(offers)

    def __str__(self):

        products_len = len(self.product) if self.product else 0
        categories_len = len(self.category) if self.category else 0
        offers_len = len(self.offer) if self.offer else 0

        return f"JsonConverter: products: {products_len}, " \
               f"categories: {categories_len}, " \
               f"offers: : {offers_len}"


input_product_category = {
    "products":
    [
        {
            "product_id_1c":"d5b92087-1ca4-11e4-8ca8-000d884fd00d",
            "model":"С-9001",
            "name":"Туфли женские",
            "description":"",
            "group_id_1c":"Женская обувь",
            "vat": "НДС 18",
            "images": ["11.jpg", "2.jpg"]
        },
        {
            "product_id_1c":"37367e5f-c600-11e7-b0ec-90004ef3f886",
            "model":"",
            "name":"Телевизор SONY",
            "description":"",
            "group_id_1c":"Телевизоры",
            "vat": "НДС 18",
            "images": ["3.jpg", "4.jpg"]
        }
    ],

    "categories":
    [
        {
            "category_id_1c":"d5b92087-1ca4-11e4-8ca8-000d884fd00d",
            "name":"Туфли женские",
            "parent_id_1c":"123"
        },
        {
            "category_id_1c":"d5b92087-1ca4-11e4-8ca8-000d884fd00d",
            "name":"Туфли женские",
            "parent_id_1c":"321"
        }
    ]
}




input_balance = {
  "message": "ВставитьСообщение",
  "login": "ВставитьЛогин",
  "password": "ВставитьПароль",
  "offers": [
    {
      "product_id_1c": "78b3494c-eb68-11ea-ab68-a451cd646eaf",
      "price": 990,
      "currency": "643",
      "price_type_id": "61502fe4-9963-11e0-9b86-f7bef2a74a60",
      "price_type_name": "Цена продажи",
      "warehouse_id_1c": "912c5d69-32e9-11e3-a958-a921bc00cf01",
      "warehouse_name": "Le Gobelin, Екатеринбург, ул. Ленина, 54/1",
      "quantity": 1000
    },
    {
      "product_id_1c": "78b34950-eb68-11ea-ab68-a451cd646eaf",
      "price": 1190,
      "currency": "643",
      "price_type_id": "61502fe4-9963-11e0-9b86-f7bef2a74a60",
      "price_type_name": "Цена продажи",
      "warehouse_id_1c": "912c5d69-32e9-11e3-a958-a921bc00cf01",
      "warehouse_name": "Le Gobelin, Екатеринбург, ул. Ленина, 54/1",
      "quantity": 4
    },
    {
      "product_id_1c": "78b34954-eb68-11ea-ab68-a451cd646eaf",
      "price": 1190,
      "currency": "643",
      "price_type_id": "61502fe4-9963-11e0-9b86-f7bef2a74a60",
      "price_type_name": "Цена продажи",
      "warehouse_id_1c": "912c5d69-32e9-11e3-a958-a921bc00cf01",
      "warehouse_name": "Le Gobelin, Екатеринбург, ул. Ленина, 54/1",
      "quantity": 4
    },
    {
      "product_id_1c": "78b34957-eb68-11ea-ab68-a451cd646eaf",
      "price": 990,
      "currency": "643",
      "price_type_id": "61502fe4-9963-11e0-9b86-f7bef2a74a60",
      "price_type_name": "Цена продажи",
      "warehouse_id_1c": "912c5d69-32e9-11e3-a958-a921bc00cf01",
      "warehouse_name": "Le Gobelin, Екатеринбург, ул. Ленина, 54/1",
      "quantity": 1
    },
    {
      "product_id_1c": "10d0e941-ff0d-11ea-ab69-9a86ec7af8a9",
      "price": 490,
      "currency": "643",
      "price_type_id": "61502fe4-9963-11e0-9b86-f7bef2a74a60",
      "price_type_name": "Цена продажи",
      "warehouse_id_1c": "912c5d69-32e9-11e3-a958-a921bc00cf01",
      "warehouse_name": "Le Gobelin, Екатеринбург, ул. Ленина, 54/1",
      "quantity": -1
    }
  ]
}

