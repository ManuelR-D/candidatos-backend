# Senate Database

Base de datos PostgreSQL para el seguimiento de sesiones del Senado.

## Inicio Rápido

### Levantar la base de datos

```bash
cd src/bdd
docker-compose up -d
```

### Detener la base de datos

```bash
docker-compose down
```

### Detener y eliminar datos

```bash
docker-compose down -v
```

## Configuración de Conexión

- **Host**: localhost
- **Puerto**: 5433
- **Usuario**: senate_user
- **Contraseña**: senate_pass
- **Base de datos**: senate_db

### String de Conexión

```
postgresql://senate_user:senate_pass@localhost:5433/senate_db
```

## Esquema de Base de Datos

El schema incluye las siguientes tablas:

- **Province**: Provincias
- **Party**: Partidos políticos
- **Representative**: Representantes/Senadores
- **SenateSession**: Sesiones del Senado
- **Topic**: Temas tratados en las sesiones
- **Attendance**: Tipos de asistencia (lookup table)
- **AttendanceSession**: Registro de asistencia por sesión
- **Vote**: Tipos de votos (lookup table)
- **VoteSession**: Registro de votos por sesión y tema

## Inicialización

`init.sql` Crea el schema inicial

`insert_representatives.sql` Inserta los representantes actuales

`insert_representatives_wayback` Inserta los representantes obtenidos por wayback_machine en versiones anteriores de la web del senado.