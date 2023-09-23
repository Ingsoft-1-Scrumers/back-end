from pony.orm import db_session

from entities import TarjetaDeCredito, Pasajero

# Un decorador es una función que toma otra función y la extiende sin modificarla explícitamente,
# es decir, agrega funcionalidad adicional a la función original.
# @db_session() se asegura de que una función pueda interactuar con la base de datos de manera 
# adecuada antes y después de su ejecución. Mas especificamente, el decorador db_session() realiza

#  - Si la función genera una excepción, se realiza un rollback de la transacción.
#  - Si la función modifica datos y no genera excepciones, se realiza un commit de la transacción.
#  - Se devuelve la conexión a la base de datos al pool de conexiones.
#  - Se limpia la cache de la sesión de la base de datos.

# Es decir, que nosotros podemos llamar a una funcion sin tener que preocuparnos por hacer commits o rollbacks.
# en la base de datos. 

# Hay dos formas de usar el decorador db_session:

@db_session
def cargar_datos_con_decoradores():
    pasajeros = [
        ('John', 20, 1234),
        ('Mary', 30, 1234555),
        ('Bob', 40, 323232),
    ]
    for nombre, edad, numero in pasajeros:
        pasajero = Pasajero(nombre=nombre, edad=edad)
        TarjetaDeCredito(numero=numero, pasajero=pasajero)


def cargar_datos_con_with():
    pasajeros = [
        ('Juan', 20, 777777),
        ('Maria', 30, 88888),
        ('Bobito', 40, 999999),
    ]

    # Esta forma permite tener commits dentro de la misma función.
    with db_session:
        for nombre, edad, numero in pasajeros:
            pasajero = Pasajero(nombre=nombre, edad=edad)
            TarjetaDeCredito(numero=numero, pasajero=pasajero)

# Si nosotros modificamos un dato de la base de datos, por ejemplo:
# tarjeta = TarjetaDeCredito.get(numero=1234)
# tarjeta.numero = 123456
# Esto no se va a guardar en la base de datos hasta que hagamos un commit.
# Si queremos hacer un commit manualmente podemos hacer:
# commit()

# Las queries son un objeto de la clase Query, para mas info ver:
# https://docs.ponyorm.org/api_reference.html#pony.orm.core.Query

# Se pueden usar las queries para obtener listas de Entidades, por ejemplo:
# pasajeros = Pasajero.select() # Devuelve una lista de todos los pasajeros
# list = select(p for p in Pasajero if p.edad > 20)[:] # Devuelve una lista de pasajeros mayores de 20 años
# Apartir de esto podemos buscar objetos en una clase especifica.

# Con el método get sobre una entidad podemos buscar por atributo. Si existe más de una entidad que 
# satisface el criterio habrá un error. Si no existe estidad la función no devulve nada:
# Pasajero.get(nombre="Bobito") # Solo existe un Bobito --> Usarlo para buscar por PrimaryKey