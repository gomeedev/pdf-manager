# PDF Manager

<div align="left">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://supabase.com/"><img src="https://img.shields.io/badge/Supabase-%23000000.svg?logo=supabase&logoColor=3ECF8E" alt="Supabase" /></a>
  <a href="https://groq.com/"><img src="https://img.shields.io/badge/Groq-f55036?logo=groq&logoColor=white" alt="Groq" /></a>
</div>

## Descripción del Proyecto
Aplicación web SaaS para gestión inteligente de PDFs. El diferenciador central es un **Agente de IA (ReAct)** que opera sobre los PDFs mediante lenguaje natural, permitiendo a los usuarios evitar la navegación manual por menús al simplemente describir la acción que necesitan (por ejemplo: "Extrae las páginas 1 y 20 y comprímelas").

## Stack Técnico
### Backend
- **Lenguaje:** Python (>=3.12)
- **Gestor de dependencias:** `uv`
- **Framework Web:** FastAPI
- **Arquitectura:** Arquitectura Hexagonal (Ports & Adapters)
- **Base de Datos & Storage & Auth:** Supabase (PostgreSQL)
- **Tratamiento de PDF:** pypdf + pymupdf
- **IA LLM:** Groq SDK (Llama 3.3-70b-versatile)

## Arquitectura Hexagonal
El backend está implementado con principios de Clean Architecture y estructurado mediante "Puertos y Adaptadores" para aislar la lógica core del ecosistema externo:
- **Core (`core/`):** Contiene la Lógica de Dominio (`domain`), Servicios orquestadores (`services`), y las Clases y Configuraciones globales (`config.py`, `security.py`).
- **Puertos (`core/ports/`):** Contratos (Interfaces) abstractos para interactuar con librerías de terceros, DB y Storage, sin casar el código base a la infraestructura.
- **Adaptadores Inbound (`adapters/inbound/`):** Las rutas HTTP de FastAPI exponiendo el sistema a interacciones web.
- **Adaptadores Outbound (`adapters/outbound/`):** La implementación particular de los puertos. Aquí interactuamos con el SDK de Supabase para Auth, Database y Storage.

## Flujo del Agente ReAct
El Agente de Inteligencia Artificial usa el modelo ReAct ("Reasoning and Acting"). Implementa el siguiente ciclo:
1. **Reason:** Evalúa la petición del usuario y el contexto histórico.
2. **Act:** Selecciona la herramienta correcta a ejecutar ("Tools" inyectadas al prompt) según lo razonado, tales como `list_pdfs`, `merge_pdfs`, `split_pdf`, `remove_pages`, `compress_pdf`, etc.
3. **Observe:** Observa el resultado que devuelve FastAPI al ejecutar las "Tools", evaluándolo y retornando el status verbal (mensaje al usuario final) u observando que debe volver a reintentar hasta un máximo de 5 iteraciones.

## Cómo correr localmente
1. **Instalar dependencias:** 
   Se recomienda usar `uv` como gestor de paquetes. Dentro de la carpeta base, ejecuta:
   ```bash
   uv sync
   # O si usas un venv manualmente: python -m pip install -r requirements.txt (o uv pip install ...)
   ```
2. **Configurar el entorno:**
   Copia el archivo `.env.example` o crea un archivo `.env` en el directorio raíz. Debes proporcionar un `SUPABASE_URL`, tus claves de `SUPABASE_ANON` y `SERVICE`, tu `GROQ_API_KEY`.
3. **Levantar el servicio:**
   Puedes iniciar el servidor a través del script de desarrollo local con uv:
   ```bash
   uv run dev.py
   ```

## Endpoints Disponibles
La API ofrece los siguientes endpoints:

- `GET /health` : Healthcheck del servicio.
- `GET /api/v1/pdfs` : Lista de PDFs asociadas al usuario.
- `DELETE /api/v1/pdfs/{pdf_id}` : Elimina y purga de la BD y del almacenamiento por completo un archivo PDF.

**Operaciones (Todas devuelven un nuevo PDF resultante):**
- `POST /api/v1/pdf-ops/upload` : Sube un nuevo PDF.
- `POST /api/v1/pdf-ops/merge` : Combina varios PDFs.
- `POST /api/v1/pdf-ops/split` : Extrae de un PDF una lista iterativa de páginas pasadas.
- `POST /api/v1/pdf-ops/compress` : Comprime en tamaño un PDF.
- `POST /api/v1/pdf-ops/remove-pages` : Elimina páginas de un arreglo indicado.

**Agente IA:**
- `POST /api/v1/agent/chat` : Interactúa por texto y conversa con el agente, anexando al ciclo un `messages_history`.
