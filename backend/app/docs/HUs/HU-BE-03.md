SYSTEM INSTRUCTION:
Actúa como un Desarrollador Backend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-BE-03
Work Item Type: User Story
Title: Exponer datos del perfil del usuario autenticado 
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\BackEnd
Iteration: PoC\Sprint 1
Tags: [Python, FastAPI, MongoDB, Hexagonal, Auth]

DESCRIPTION:
Como **Frontend**,
Quiero **obtener los datos del usuario actual a través de un endpoint protegido**,
Para **mostrar el nombre y estado en el Dashboard.**

ACCEPTANCE CRITERIA:
1. **Endpoint Protegido (`GET /users/me`):**
   - **Autenticación:** El endpoint DEBE rechazar peticiones sin Header `Authorization: Bearer <access_token>` válido.
   - **Validación de Token:**
     - Verificar firma JWT con clave pública RS256.
     - Verificar expiración (`exp` claim).
     - Verificar tipo de token (`type: "access"`). Rechazar `temp` o `refresh` tokens.
   - **Errores de Autenticación:**
     - `401 Unauthorized` si no hay token, token inválido, expirado o tipo incorrecto.
     - Mensaje específico: "Missing token" | "Invalid token" | "Expired token" | "Invalid token type".

2. **Consulta a MongoDB:**
   - Extraer `sub` (user_id) del payload JWT.
   - Buscar documento en colección `users` por `_id` (ObjectId).
   - **Capacidad de Búsqueda:** Extender el repositorio de usuarios para permitir búsqueda por identificador único (además de las búsquedas existentes por teléfono y email).
   - Si no se encuentra el usuario → `404 Not Found` (caso edge: usuario eliminado después de login).

3. **Sanitización de Respuesta:**
   - **Campos Incluidos:**
     - `user_id`: String (ObjectId convertido a string).
     - `phone`: String (formato E.164).
     - `email`: String o null (si no proporcionado).
     - `name`: String o null (si no proporcionado).
     - `kyc_status`: String ("pending" | "approved" | "rejected").
     - `mfa_enabled`: Boolean.
     - `created_at`: String (ISO 8601 format, ej: "2026-01-30T14:23:45.123Z").
   - **Campos EXCLUIDOS (seguridad):**
     - `password_hash`: NUNCA debe retornarse.
     - `mfa_secret`: NUNCA debe retornarse (si se implementa TOTP real).
     - Cualquier campo interno no relevante para el frontend.

4. **Middleware de Autenticación:**
   - Crear middleware reutilizable `JWTAuthMiddleware` o dependency `get_current_user` que:
     - Extrae token del header `Authorization`.
     - Valida firma, expiración y tipo.
     - Retorna user_id (sub) o lanza HTTPException.
   - Este middleware será reutilizado en futuros endpoints protegidos.

5. **Performance:**
   - Índice en `_id` es automático en MongoDB (no requiere acción).
   - Considerar caché de usuarios en memoria (Redis) para reducir latencia en futuros sprints.

6. **Contrato OpenAPI:**

```yaml
GET /users/me
Summary: Obtener perfil del usuario autenticado
Security:
  - BearerAuth: []

Headers:
  Authorization: Bearer <access_token> (requerido)

Responses:
  200 OK:
    {
      "user_id": "string (ObjectId, ej: 507f1f77bcf86cd799439011)",
      "phone": "string (formato E.164, ej: +573001234567)",
      "email": "string | null (ej: user@example.com)",
      "name": "string | null (ej: Juan Pérez)",
      "kyc_status": "string (pending | approved | rejected)",
      "mfa_enabled": "boolean",
      "created_at": "string (ISO 8601, ej: 2026-01-30T14:23:45.123Z)"
    }
  
  401 Unauthorized (Missing Token):
    {
      "detail": "Missing authorization token"
    }
  
  401 Unauthorized (Invalid Token):
    {
      "detail": "Invalid token signature"
    }
  
  401 Unauthorized (Expired Token):
    {
      "detail": "Token has expired"
    }
  
  401 Unauthorized (Wrong Token Type):
    {
      "detail": "Invalid token type, access token required"
    }
  
  404 Not Found:
    {
      "detail": "User not found"
    }
```

DEINITION OF READY
1. ✅ Esquema de respuesta JSON para "Perfil de Usuario" definido (ver Acceptance Criteria #3).
2. ✅ Middleware de validación de JWT implementado en HU-BE-02 (dependency `get_current_user`).
3. ✅ Claves públicas RS256 disponibles para validación de firma (generadas en HU-BE-02).

DEFINITION OF DONE (Global Policy):
1. **Formato:** Código formateado con **Black** e **Isort**.
2. **Linting:** Sin errores de **Ruff**.
3. **Typing:** **Mypy** en modo estricto pasando al 100%.
4. **Complejidad:** Complejidad Ciclomática < 10 por función.
5. **Cobertura de Pruebas:** >= 85% en líneas, statements, funciones y branches.
6. **Tipos de Tests:** Incluir casos positivos, negativos, edge cases, transiciones de estado y casos de integración (ver BACKEND-GUIDELINES.md sección 5.3.2).
7. **Docs:** Todos los métodos públicos documentados con **Google Docstrings**.
8. **Límites:** Ningún archivo excede las 500 líneas.
9. **Validación Local:** Ejecutar `black`, `isort`, `ruff`, `radon cc`, `mypy` y `pytest --cov` antes de commit.
10. Endpoint funcional probado con Postman/httpx.
11. Test manual verificando que `password_hash` y `mfa_secret` NO se exponen en la respuesta.
12. Test automatizado que verifica que la respuesta JSON NO contiene claves sensibles (`assert 'password_hash' not in response.json()`).
13. Test de integración con tokens válidos, expirados, inválidos y tipos incorrectos.


-----------------------------------------------------------------------
⚠️ CRITICAL INSTRUCTIONS - READ BEFORE STARTING:

1. **DO NOT DELETE CONFIGURATION FILES:**
   - `Backend/tests/conftest.py` (required for pytest imports)
   - `PoC/.gitignore` (project-wide ignore rules)
   - ANY file in `Backend/` root that ends in `.toml`, `.ini`, `.cfg`, `.json`
   - If you think a config file should be removed, STOP and ask first.

2. **MANDATORY REFERENCES:**
   - Read `Backend/docs/BACKEND-GUIDELINES.md` sections 5.1 (Patterns) and 5.3 (Testing) BEFORE coding.
   - Read `agents.md` section 5.1.7.1 for test type requirements and examples.
   - Follow Hexagonal Architecture: domain → application → infrastructure adapters.

3. **QUALITY GATES (BLOCKERS):**
   - Coverage >= 85% (pytest --cov)
   - All 6 test types implemented: positive, negative, edge cases, state transitions, concurrency, integration.
   - Complexity < 10 per function (check with radon cc).
   - All DoD checks passing before committing.

4. **TESTING FRAMEWORK:**
   - Use PyTest + pytest-asyncio + pytest-cov (NOT unittest).
   - Pattern: AAA (Arrange-Act-Assert).
   - Name tests: `test_<unit>_when_<condition>_then_<expected>`.

-----------------------------------------------------------------------
YOUR TASK:
1. Analiza los archivos actuales del repositorio.
2. Genera el código necesario para completar este Work Item.
3. Genera los tests correspondientes (6 tipos obligatorios).
4. Asegúrate que el código entregado cumple con los Definition of Done detallados en el Work Item.
5. Ejecuta validación local: `black .`, `isort .`, `ruff check .`, `radon cc`,  `mypy .`, `pytest --cov`.
6. Confirma qué archivos has creado o modificado.