# La Cosa, Back-end

Back-end de una versión online del juego de mesa La Cosa (The Thing), desarrollado como proyecto grupal de Ingeniería de Software (tercer año) en FaMAF, Universidad Nacional de Córdoba, siguiendo una metodología Scrum. Construido con FastAPI (Python).

## El juego

La Cosa es un juego de mesa de roles ocultos y deducción social. Este repositorio implementa la lógica del juego y la API que consume el front-end. Las reglas del juego original están [disponibles acá](https://genxgames.es/wp-content/uploads/the-thing-reglas.pdf).

## Tecnologías

- FastAPI
- Python 3.10
- WebSockets
- MySQL

## Instalación

Vamos a trabajar con Python 3.10, ejecutamos los siguientes comandos:

```bash
$ sudo apt update && sudo apt upgrade -y
$ sudo apt install python3.10
$ sudo apt install python3-pip
$ python3.10 --version
Python 3.10.12
```

FastAPI genera la documentación interactiva de la API sola, disponible en `/docs` (Swagger UI) una vez que la API está corriendo.

## Crear entorno virtual

Vamos a crear un entorno virtual para instalar las dependencias de nuestro proyecto. En el directorio `home` ejecutamos el nombre del entorno virtual`venv` y cada vez que queremos trabajar en el proyecto ejecutamos `source venv/bin/activate` para activar el entorno virtual.

```bash
$ python3 -m venv venv
$ source venv/bin/activate 
(venv) $ cd /path/to/back-end/directory
(venv) $ pip install -r requirements.txt
```

En el archivo `requirements.txt` se encuentran todas las librerias que vamos a utilizar en el back-end.

## Variables de entorno

Agregar variables de entorno `variable` en el proyecto y el `PYTHONPATH` para poder correr el servidor y los tests:

```bash
(venv) $ cd /path/to/back-end/directory/src
(venv) $ export ENVIRONMENT="variable"
(venv) $ export PYTHONPATH="/path/to/back-end/directory/src"
```

Valores de `variable` dependiendo de la etapa de desarrollo. Cada una va a tener una base de datos diferente:

- `development`
- `test`
- `production`

## Correr el servidor

Se les proporciona un Makefile con el que pueden correr la aplicacion. Correr el comando:

```bash
(venv) $ make run_app
```

## Repositorios del proyecto

- Back-end (este repositorio)
- [Front-end](https://github.com/Ingsoft-1-Scrumers/front-end) (React + Vite)
