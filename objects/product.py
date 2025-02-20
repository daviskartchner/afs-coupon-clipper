class Product:
    def __init__(self, item):
        self.upc = item['UPC']
        self.description = item['Description']
        self.size = item['SizeAlpha']