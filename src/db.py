from tinydb import TinyDB, Query
from datetime import datetime
import os


class Database:
    def __init__(self, db_path="data.json"):
        dirname = os.path.dirname(db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.db = TinyDB(db_path)
        self.products = self.db.table("products")

    def insert_product(self, product_data):
        product_data["created_at"] = datetime.now().isoformat()
        return self.products.insert(product_data)

    def get_product(self, asin):
        Product = Query()
        return self.products.get(Product.asin == asin)

    def get_all_products(self):
        return self.products.all()

    def search_products(self, search_criteria):
        Product = Query()
        query = None
        for key, value in search_criteria.items():
            if query is None:
                query = (Product[key] == value)
            else:
                query &= (Product[key] == value)

        return self.products.search(query) if query else []