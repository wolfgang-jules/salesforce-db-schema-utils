# salesforce-db-schema-utils

Utilidades en Python para trabajar con esquemas de Salesforce:

- `get-current-table-schema`: consulta `FieldDefinition` y exporta el esquema actual de una tabla a CSV.
- `generate-new-table-schema`: propone nuevos nombres de campos (`snake_case`) y valida resultados.

## Requisitos

- Python 3.11 o superior
- Acceso a Salesforce API con usuario, password y security token

## Estructura

```text
.
|-- get-current-table-schema/
|   |-- main.py
|   |-- .env.example
|   |-- queries/field_definition.sql
|   `-- salesforce_tables/           # CSVs generados (ignorado por git)
|-- generate-new-table-schema/
|   |-- module.py
|   |-- process_file.py
|   |-- validate_file.py
|   |-- input_files/
|   `-- output_files/                # CSVs generados (ignorado por git)
|-- .gitignore
`-- requirements.txt
```

## Instalacion

En PowerShell, desde la raiz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Variables de entorno

Copia `get-current-table-schema/.env.example` a `get-current-table-schema/.env` y completa valores reales:

```dotenv
SALESFORCE_USERNAME=tu_usuario
SALESFORCE_PASSWORD=tu_password
SALESFORCE_SECURITY_TOKEN=tu_security_token
SALESFORCE_DOMAIN=login
SALESFORCE_TABLE_NAME=BomItem__c
```

Notas:

- `SALESFORCE_DOMAIN` es obligatorio y se lee desde `get-current-table-schema/.env`.
- `SALESFORCE_DOMAIN=login` para produccion.
- `SALESFORCE_DOMAIN=test` para sandbox.
- `SALESFORCE_TABLE_NAME` tambien es obligatorio y define la tabla a exportar.
- `get-current-table-schema/.env` esta ignorado por git para evitar exponer secretos.

## Uso

1. Exportar esquema actual de Salesforce:

```powershell
python get-current-table-schema/main.py
```

Resultado: archivo CSV en `get-current-table-schema/salesforce_tables/`.

2. Generar propuesta de nuevos nombres:

```powershell
python generate-new-table-schema/process_file.py
```

Resultado: archivo CSV timestamped en `generate-new-table-schema/output_files/`.

3. Validar resultado generado:

```powershell
python generate-new-table-schema/validate_file.py
```

## Dependencias

Las dependencias directas del proyecto estan en `requirements.txt`.
