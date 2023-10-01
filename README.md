# Back-end

## Instalación

Vamos a trabajar con Python 3.10, ejecutamos los siguientes comandos:

```bash
$ sudo apt update && sudo apt upgrade -y
$ sudo apt install python3.10
$ sudo apt install python3-pip
$ python3.10 --version
Python 3.10.12
```

## Crear entorno virtual

Vamos a crear un entorno virtual para instalar las dependencias de nuestro proyecto. En el directorio `home` ejecutamos:
El nombre del entorno virtual es `venv`, se ejecuta una sola vez y cada vez que queremos trabajar en el proyecto ejecutamos `source venv/bin/activate` para activar el entorno virtual.

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

## Pagina para probar nuestra API

Esta [pagina web](https://reqbin.com/) que te permite hacer requests HTTP a la API. Se necesita tener Chrome + esta [Extensión](https://chrome.google.com/webstore/detail/reqbin-http-client/gmmkjpcadciiokjpikmkkmapphbmdjok) instalada para poder usarla.
