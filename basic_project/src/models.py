from pony.orm import Database, Required

from settings import DATABASE_FILENAME

# Configuración de la base de datos
db = Database()

# Aca van todas las entidades de la base de datos de nuestro proyecto.

# Define la entidad Product
class Product(db.Entity):
    name = Required(str)
    price = Required(float)


# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)

# Genera las tablas en la base de datos
db.generate_mapping(create_tables=True)
