# Testing

## Antes de correr los tests

Si se utiliza el MakeFile proporcionado por los profes para correr los tests, se debe correr estos comandos antes de ejecutar el MakeFile:

```bash
(venv) $ cd /path/to/back-end/directory/src
(venv) $ export ENVIRONMENT="test"
(venv) $ export PYTHONPATH="/path/to/back-end/directory/src/tests"
```

## Comandos para correr los tests

Pararse en el directorio `src` y ejecutar los siguientes comandos de acuerdo al tipo de test. Si salta un error de module not found, agregar un archivo vacio `__init__.py` en el directorio `tests` y volver a ejecutar el comando.

Para correr unit tests:

```bash
make run_unit_tests
```

Para correr integration tests:

```bash
make run_integration_tests
```

Para correr end to end tests. Primero hay que levantar el servidor con `ENVIRONMENT="test"` y luego ejecutar:

```bash
make run_end2end_tests
```

Se necesita tener conexion a internet para correr los tests end to end.
