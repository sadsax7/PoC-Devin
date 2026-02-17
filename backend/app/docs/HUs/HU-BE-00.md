SYSTEM INSTRUCTION:
Actúa como un Desarrollador Backend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-BE-00
Work Item Type: User Story
Title: Configurar andamiaje Hexagonal y conexión asíncrona a MongoDB
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\BackEnd
Iteration: PoC\Sprint 1
Tags: [Python, FastAPI, MongoDB, Hexagonal] o [NextJS, AtomicDesign, Tailwind]

DESCRIPTION:
Como **Desarrollador Backend**,
Quiero **establecer la estructura de carpetas del proyecto y la conexión a la base de datos MongoDB**,
Para **tener una base sólida donde implementar los repositorios de usuarios sin deuda técnica inicial.**

ACCEPTANCE CRITERIA:
1.  **Estructura:** Carpetas creadas siguiendo patrón hexagonal: `domain` (entidades/puertos), `application` (casos de uso), `infrastructure` (adapters/controllers).
2.  **Base de Datos:** Configuración de cliente MongoDB asíncrono (Motor o Beanie) funcional.
3.  **Configuración:** Archivo `.env` configurado para credenciales y secrets (no hardcoded).
4.  **Health Check:** Endpoint `GET /health` que retorne `200 OK` y confirme ping exitoso a Mongo.

DEINITION OF READY
1. Repositorio Git creado y accesible por el equipo.
2. Acceso a instancia de MongoDB (local o Atlas) verificado.
3. Versión de Python (3.11+) y Stack (FastAPI, Motor) definidos.

DEFINITION OF DONE (Global Policy):
1. **Formato:** Código formateado con **Black** e **Isort**.
2. **Linting:** Sin errores de **Flake8** o **Ruff**.
3. **Typing:** **Mypy** en modo estricto pasando al 100%.
4. **Complejidad:** Complejidad Ciclomática (Radon) < 10 por función.
5. **Pruebas:** Pipeline de CI básico ejecutándose sin errores.
6. **Docs:** Archivos base con **Google Docstrings** para configuración.
7. **Límites:** Ningún archivo de configuración excede las 500 líneas.
8. Inicia el servicio API y la BD correctamente.

-----------------------------------------------------------------------
YOUR TASK:
1. Analiza los archivos actuales del repositorio.
2. Genera el código necesario para completar este Work Item.
3. Genera los tests correspondientes.
4. Asegúrate que el código entregado cumple con los Definition of Done detallados en el Work Item
5. Confirma qué archivos has creado o modificado.