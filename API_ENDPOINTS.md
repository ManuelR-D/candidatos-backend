# API Endpoints Documentation

Esta documentación describe todos los endpoints expuestos por los controladores de la API del sistema de Senado.

## Tabla de Contenidos
- [Representative Controller](#representative-controller)
- [Session Controller](#session-controller)
- [Topic Controller](#topic-controller)

---

## Representative Controller

**Base URL**: Puerto por defecto `5002`

### Health Check

**GET** `/health`

Verifica el estado del servicio de representantes.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "representative-api"
}
```

---

### Obtener Todos los Representantes

**GET** `/api/representatives`

Obtiene una lista de todos los representantes con filtros opcionales.

**Query Parameters:**
- `province` (opcional): Filtrar por nombre de provincia
- `party` (opcional): Filtrar por nombre de partido
- `coalition` (opcional): Filtrar por nombre de coalición

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "representatives": [
      {
        "id": "uuid",
        "full_name": "string",
        "first_name": "string",
        "last_name": "string",
        "province": "string",
        "party": "string",
        "coalition": "string"
      }
    ],
    "total": 0
  }
}
```

**Respuesta de Error (500):**
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve representatives"
}
```

---

### Obtener Sesiones de un Representante

**GET** `/api/representatives/<representative_id>/sessions`

Obtiene todas las sesiones del Senado donde un representante participó.

**Path Parameters:**
- `representative_id`: UUID del representante

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "representative_id": "uuid",
    "sessions": [
      {
        "session_id": 0,
        "date": "YYYY-MM-DD"
      }
    ],
    "total": 0
  }
}
```

**Respuesta de Error (500):**
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve representative sessions"
}
```

---

### Obtener Temas de un Representante

**GET** `/api/representatives/<representative_id>/topics`

Obtiene todos los temas donde un representante tiene intervenciones.

**Path Parameters:**
- `representative_id`: UUID del representante

**Query Parameters:**
- `session_id` (opcional): Filtrar por ID de sesión del Senado

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "representative_id": "uuid",
    "session_id": 0,
    "topics": [
      {
        "topic_id": 0,
        "name": "string",
        "session_id": 0,
        "session_date": "YYYY-MM-DD",
        "intervention_count": 0
      }
    ],
    "total": 0
  }
}
```

**Respuesta de Error (500):**
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve representative topics"
}
```

---

### Obtener Intervenciones de un Representante en un Tema

**GET** `/api/representatives/<representative_id>/topics/<topic_id>/interventions`

Obtiene todas las intervenciones de un representante para un tema específico.

**Path Parameters:**
- `representative_id`: UUID del representante
- `topic_id`: ID del tema

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "representative": {
      "id": "uuid",
      "full_name": "string",
      "last_name": "string",
      "first_name": "string"
    },
    "topic": {
      "id": 0,
      "name": "string",
      "session_id": 0,
      "session_date": "YYYY-MM-DD"
    },
    "interventions": [
      {
        "intervention_id": 0,
        "text": "string",
        "role": "string",
        "order": 0
      }
    ],
    "total": 0
  }
}
```

**Respuestas de Error:**
- **404**: Representante o tema no encontrado
```json
{
  "success": false,
  "error": "Representative not found"
}
```

- **500**: Error del servidor
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve interventions"
}
```

---

## Session Controller

**Base URL**: Puerto por defecto `5000`

### Health Check

**GET** `/health`

Verifica el estado del servicio de parseo de sesiones.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "session-parser"
}
```

---

### Parsear una Sesión

**POST** `/api/sessions/parse`

Parsea un archivo PDF de sesión y lo almacena en la base de datos.

**Content-Type**: `multipart/form-data`

**Form Data:**
- `file` (requerido): Archivo PDF de la sesión
- `date` (opcional): Fecha de la sesión en formato YYYY-MM-DD (puede inferirse del nombre del archivo)
- `session_type` (opcional): Nombre corto del tipo de sesión (puede inferirse del nombre del archivo)
- `debug` (opcional): Bandera booleana para modo debug (por defecto: false)
- `force` (opcional): Bandera booleana para forzar re-parseo (por defecto: false)

**Respuesta Exitosa - Archivo ya parseado (200):**
```json
{
  "success": true,
  "message": "File already parsed (use force=true to re-parse)",
  "already_parsed": true,
  "data": {
    "session_id": 0,
    "file_hash": "string",
    "original_file_name": "string",
    "upload_date": "YYYY-MM-DDTHH:MM:SS"
  }
}
```

**Respuesta Exitosa - Parseo completado (201):**
```json
{
  "success": true,
  "message": "Session parsed and stored successfully",
  "already_parsed": false,
  "data": {
    "session_id": 0,
    "session_date": "YYYY-MM-DD",
    "file_hash": "string",
    "topics_stored": 0,
    "interventions_stored": 0,
    "attendance_stored": 0,
    "topics_parsed": 0,
    "attendance_parsed": 0,
    "index_items": 0
  }
}
```

**Respuesta de Error (500):**
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to parse session"
}
```

**Notas:**
- Tamaño máximo de archivo: 50MB
- Si el archivo ya fue parseado, devuelve información de la sesión existente a menos que se use `force=true`
- El endpoint valida automáticamente el tipo de sesión y la fecha

---

### Obtener Sesiones

**GET** `/api/sessions`

Obtiene todas las sesiones de la base de datos.

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Endpoint not yet implemented",
  "data": []
}
```

**Nota**: Este endpoint está pendiente de implementación completa.

---

## Topic Controller

**Base URL**: Puerto por defecto `5002`

### Health Check

**GET** `/health`

Verifica el estado del servicio de temas.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "topic-controller"
}
```

---

### Obtener Temas por Representante

**GET** `/api/topics/by-representative/<representative_id>`

Obtiene todos los temas donde un representante tiene intervenciones.

**Path Parameters:**
- `representative_id`: UUID del representante

**Query Parameters:**
- `session_id` (opcional): Filtrar por ID de sesión del Senado

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "representative_id": "uuid",
    "session_id": 0,
    "topics": [
      {
        "topic_id": 0,
        "name": "string",
        "session_id": 0,
        "session_date": "YYYY-MM-DD",
        "intervention_count": 0
      }
    ],
    "total": 0
  }
}
```

**Respuestas de Error:**
- **400**: Formato de UUID inválido
```json
{
  "success": false,
  "error": "Invalid UUID format",
  "message": "string"
}
```

- **500**: Error del servidor
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve topics for representative"
}
```

---

### Obtener Tema por ID

**GET** `/api/topics/<topic_id>`

Obtiene un tema específico por su ID.

**Path Parameters:**
- `topic_id`: ID único del tema (integer)

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "UniqueID": 0,
    "Name": "string",
    "SenateSession_id": 0
  }
}
```

**Respuesta de Error (404):**
```json
{
  "success": false,
  "message": "Topic not found"
}
```

**Respuesta de Error (500):**
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve topic"
}
```

---

### Obtener Todos los Temas

**GET** `/api/topics`

Obtiene todos los temas con filtrado opcional.

**Query Parameters:**
- `session_id` (opcional): Filtrar por ID de sesión del Senado

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "data": {
    "topics": [
      {
        "UniqueID": 0,
        "Name": "string",
        "SenateSession_id": 0
      }
    ],
    "total": 0
  }
}
```

**Respuesta de Error (500):**
```json
{
  "success": false,
  "error": "string",
  "message": "Failed to retrieve topics"
}
```

---

## Configuración de Base de Datos

Todos los controladores utilizan las siguientes variables de entorno para la conexión a la base de datos:

- `DB_HOST`: Host de la base de datos (por defecto: `localhost`)
- `DB_PORT`: Puerto de la base de datos (por defecto: `5433`)
- `DB_NAME`: Nombre de la base de datos (por defecto: `senate_db`)
- `DB_USER`: Usuario de la base de datos (por defecto: `senate_user`)
- `DB_PASSWORD`: Contraseña de la base de datos (por defecto: `senate_pass`)

## Códigos de Estado HTTP8

- **200 OK**: Solicitud exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Error en los parámetros de la solicitud
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error interno del servidor

## Notas Adicionales

- Todos los endpoints registran las solicitudes entrantes en la consola
- Los endpoints que devuelven fechas utilizan el formato ISO 8601 (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
- Los IDs de representantes utilizan formato UUID
- Los IDs de sesiones y temas utilizan integers
