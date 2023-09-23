from fastapi import FastAPI, HTTPException
from product_repository import ProductRepository
from util import ProductWithDollarBluePrices
from connector import DolarBlueConnector
from requests import Timeout

app = FastAPI() # Creamos instancia de la clase FastAPI

# Definimos los endpoints de nuestra API
# Ver https://fastapi.tiangolo.com/tutorial/first-steps/ y charla de FastAPI

@app.post('/products') # Decorador que indica un endpoint
def create_product(name: str, price: float):
    repo = ProductRepository() # Instanciamos el repositorio (que es la clase que nos permite acceder a la base de datos)
    repo.create_product(name=name, price=price)
    return {'message': 'Product created'}


@app.get('/products')
def get_products():
    repo = ProductRepository()
    return repo.get_products() # Llamamos a un método del repositorio


@app.get('/products/{product_id}') # Decorador que indica un endpoint con un parámetro
def get_product(product_id: int): # Uso de type hints para indicar el tipo de dato del parámetro
    repo = ProductRepository()
    try:
        return repo.get_product(product_id) # Si sale todo bien, FastAPI devuelve el codigo 200 y el producto
    except ValueError:
        raise HTTPException(status_code=404, detail='Product not found') # Si no encuentra el producto, devuelve el codigo 404


@app.put('/products/') 
def update_products_price(factor: float):
    repo = ProductRepository()
    repo.update_all_prices(factor)
    return {'message': 'Prices updated'}


@app.get('/products_with_usd_prices/{product_id}')
def get_product_with_usd_price(product_id: int):
    repo = ProductWithDollarBluePrices(
        ProductRepository(), DolarBlueConnector()
    )
    try:
        return repo.get_product(product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Product not found')
    except Timeout:
        HTTPException(status_code=504, detail='Timeout...')


@app.get('/products_with_usd_prices/')
def get_products_with_usd_price():
    repo = ProductWithDollarBluePrices(
        ProductRepository(), DolarBlueConnector()
    )
    try:
        return repo.get_products()
    except Timeout:
        HTTPException(status_code=504, detail='Timeout...')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
