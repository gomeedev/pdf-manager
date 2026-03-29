# Planning: PDF Manager con Agente IA

## Arquitectura y Metodología
- **Framework:** FastAPI
- **Gestor de dependencias:** uv
- **Arquitectura:** Hexagonal (Ports & Adapters)
- **Patrón IA:** ReAct con Function Calling
- **Metodología:** Desarrollo por ciclos estrictos sin deuda técnica.

## Decisiones Técnicas Confirmadas
- **Prveedor LLM:** Groq (llama-3.3-70b-versatile)
- **Base de Datos & Auth:** PostgreSQL via Supabase (RLS habilitado)
- **Almacenamiento de PDFs:** Supabase Storage (S3-compatible, bucket `pdf-files` max 50MB)
- **Puerto de desarrollo:** 8000

## Flujo de Trabajo (Ciclos)
1. **Configuración del proyecto** (Git, uv, FastAPI, Hexagonal, dotenv)
2. **Arquitectura base** (ports, adapters, Integración de Auth Supabase y diseño de schema DB mediante Supabase MCP)
3. **Módulo PDF** (herramientas atómicas para manipular archivos)
4. **Agente IA** (integración ReAct + function calling Llama)
