from datetime import datetime
from pony.orm import (Database, PrimaryKey, Required, Set, Optional)


db = Database()  # Creamos el objeto db, que es una instancia de la clase Database. 
                 # Vamos a tener una sola base de datos con todos los modelos/entidades.

# Lo que sigue se puede hacer con PonyORM de manera grafica
# En nuestro proyecto, esto iria en el archivo models.py
# Lo malo es que estas bases de datos no tiene migraciones, por lo que si cambiamos algo en el modelo
# hay que borrar la base de datos y volver a crearla.

# En PonyORM, no nos interesa los metodos de las clases, sino los atributos. Los metodos que se crean
# son para modificar los atributos de la clase. Los metodos mas basicos no son necesarios definirlos.
# Solamente hay que definir los metodos que tengan una logica mas compleja.

class Pasajero(db.Entity): # db.Entity es una clase de PonyORM que representa una tabla en la base de datos.
                           # es decir, que Pasajero es una subclase de db.Entity
    id = PrimaryKey(int, auto=True) # auto=True significa que se genera automaticamente (autoincremental)
    nombre = Required(str) # Required significa que es obligatorio
    edad = Required(int) 
    reservas = Set('Reserva') # Set significa que es una relacion de uno a muchos o muchos a muchos con la entidad Reserva
    tarjeta_de_creditos = Set('TarjetaDeCredito')


class Habitacion(db.Entity):
    id = PrimaryKey(int, auto=True)
    Pax = Required(int)
    reservas = Set('Reserva') 


class Reserva(db.Entity):
    id = PrimaryKey(int, auto=True) 
    habitacion = Required(Habitacion)
    pasajero = Required(Pasajero) # Con esto se crea una relacion de muchos a uno con la entidad Pasajero
    estado = Required(str)
    ingreso = Required(datetime)
    egreso = Required(datetime)
    fecha_cancelacion = Optional(datetime) # Optional significa que es opcional
    factura = Optional('Factura')


class TarjetaDeCredito(db.Entity):
    id = PrimaryKey(int, auto=True)
    numero = Required(int)
    vencimiento = Optional(datetime)
    pasajero = Required(Pasajero)


class Factura(db.Entity):
    id = PrimaryKey(int, auto=True)
    reserva = Required(Reserva)
    monto = Optional(float)


# OTROS EJEMPLOS

class Materia(db.Entity):
    nombre = Required(str)
    profesores = Set("Profesor")


class Profesor(db.Entity):
    nombre = Required(str)
    materias = Set(Materia)

# Conectamos el objeto `db` con la base de dato.
db.bind('sqlite', 'example.sqlite', create_db=True) # create_db=True significa que si la base de datos no existe, la crea.
# Generamos las base de datos.
db.generate_mapping(create_tables=True) # create_tables=True significa que si las tablas no existen, las crea.
