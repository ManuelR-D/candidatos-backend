# Candidatos-backend

Este servicio es capaz de parsear las sesiones taquigraficas del senado, obtener las intervenciones de los senadores por topic y generar resumenes por IA.

## Setup

```
git clone https://github.com/ManuelR-D/candidatos-back
cd candidatos-back/src/bdd
docker-compose up -d
./import_representatives.ps1

cd ../
python install -r requirements.txt
python run_api_server.py
```

```
cd candidatos-back/sessions
# La ingesta iniciar puede tardar mucho tiempo! Incluye los resumenes hechos por IA. Requiere llenar el .env
./ingest.ps1 -Year 2025
./ingest.ps1 -Year 2026
```

## Bdd

Leer `./src/bdd/README.md` para más información sobre el setup de la base de datos y su schema
