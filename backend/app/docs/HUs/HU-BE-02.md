SYSTEM INSTRUCTION:
Actúa como un Desarrollador Backend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-BE-02
Work Item Type: User Story
Title: Implementar login, emisión de JWT y endpoint de verificación MFA  
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\BackEnd
Iteration: PoC\Sprint 1
Tags: [Python, FastAPI, MongoDB, Hexagonal, Auth]

DESCRIPTION:
Como **Sistema de Seguridad**,
Quiero **validar credenciales contra MongoDB y gestionar el flujo de autenticación (Login + MFA)**,
Para **garantizar acceso seguro y emitir tokens de sesión válidos.**

ACCEPTANCE CRITERIA:
1. **Endpoint Login (`POST /auth/login`):**
   - **Input:** `phone` (formato E.164, ej: +573001234567) y `password` (string, 8-128 caracteres).
   - **Validación de Contraseña:** Usar **Argon2** para verificar hash contra `password_hash` almacenado.
   - **Flujo de MFA:**
     - Si `mfa_enabled: false` → Retornar `200 OK` con `access_token` (JWT final) y `refresh_token`.
     - Si `mfa_enabled: true` → Retornar `200 OK` con `temp_token` (JWT de corta duración, 5 min) y `mfa_required: true`.
   - **Manejo de Errores:**
     - `404 Not Found` si el teléfono no existe en la colección `users`.
     - `401 Unauthorized` si la contraseña es incorrecta.
     - `423 Locked` si el usuario tiene `kyc_status: "rejected"` (usuario bloqueado).

2. **Endpoint MFA (`POST /auth/mfa/verify`):**
   - **Input:** `temp_token` (JWT de login con MFA) y `code` (string de 6 dígitos).
   - **Mock MFA:** Código fijo **"123456"** aprueba la verificación (simula TOTP real).
   - **Flujo:**
     - Validar `temp_token` (verificar firma, expiración y claim `mfa_pending: true`).
     - Si `code == "123456"` → Retornar `200 OK` con `access_token` (JWT final) y `refresh_token`.
     - Si `code != "123456"` → Retornar `401 Unauthorized` con mensaje "Invalid MFA code".
   - **Protección contra Fuerza Bruta:**
     - Después de 3 intentos fallidos de verificación MFA para el mismo usuario, retornar `429 Too Many Requests`.
     - Implementar contador en memoria que rastrea intentos por usuario.
     - Limpiar contador después de verificación exitosa o después de 5 minutos de inactividad.
     - Mensaje de error: "Too many failed MFA attempts, please login again".

3. **JWT Claims y Seguridad:**
   - **Access Token:**
     - `sub`: ObjectId del usuario (string).
     - `phone`: Teléfono del usuario.
     - `exp`: 30 minutos (1800 segundos).
     - `type`: "access"
   - **Refresh Token:**
     - `sub`: ObjectId del usuario.
     - `exp`: 7 días (604800 segundos).
     - `type`: "refresh"
   - **Temp Token (MFA pending):**
     - `sub`: ObjectId del usuario.
     - `mfa_pending`: true.
     - `exp`: 5 minutos (300 segundos).
     - `type`: "temp"
   - **Algoritmo:** RS256 (clave pública/privada). Claves generadas con `openssl` y almacenadas en `.env` (privada) y `/public/jwks.json` (pública, para futura validación por servicios externos).

4. **Componentes de Gestión de Seguridad:**
   - **Generación y Validación de Tokens:**
     - Crear componente encargado de generar tokens de acceso, renovación y temporales con los claims especificados.
     - Validar firma digital, tiempo de expiración y tipo de token en cada petición.
     - Usar claves asimétricas RS256 generadas con herramientas criptográficas estándar.
   - **Verificación de Códigos MFA:**
     - Crear componente que valida códigos de autenticación de dos factores.
     - En esta fase, usar código fijo "123456" como simulación (preparar para futura integración con TOTP real).

5. **Índices de Rendimiento:**
   - Índice en `phone` (único) ya creado en HU-BE-01.
   - Considerar índice en `created_at` si se implementan consultas de auditoría.

6. **Auditoría y Logs:**
   - **Eventos de Inicio de Sesión:**
     - Registrar intentos exitosos con identificador de usuario, marca de tiempo y dirección IP (usar valor simulado '127.0.0.1' en PoC).
     - Registrar intentos fallidos con teléfono, razón del fallo ("wrong_password" | "user_not_found" | "account_locked") y marca de tiempo.
   - **Eventos de MFA:**
     - Registrar verificaciones exitosas y fallidas de códigos MFA.
   - **Formato de Logs:**
     - Usar formato estructurado (JSON) con campos consistentes: `event`, `user_id`, `timestamp`, `reason`, `ip`.
   - **Seguridad de Logs:**
     - **PROHIBIDO:** Registrar contraseñas, hashes de contraseñas o tokens completos.
     - Si es necesario referenciar un token para debugging, registrar solo los últimos 4 caracteres.

7. **Contrato OpenAPI:**

```yaml
POST /auth/login
Summary: Iniciar sesión con teléfono y contraseña
Request Body (application/json):
  {
    "phone": "string (requerido, formato E.164: +[código_país][número])",
    "password": "string (requerido, 8-128 caracteres)"
  }

Responses:
  200 OK (MFA Disabled):
    {
      "access_token": "string (JWT con exp 30 min)",
      "refresh_token": "string (JWT con exp 7 días)",
      "token_type": "Bearer",
      "expires_in": 1800
    }
  
  200 OK (MFA Enabled):
    {
      "temp_token": "string (JWT con exp 5 min, claim mfa_pending: true)",
      "mfa_required": true,
      "message": "MFA verification required"
    }
  
  401 Unauthorized:
    {
      "detail": "Invalid credentials"
    }
  
  404 Not Found:
    {
      "detail": "Phone number not registered"
    }
  
  423 Locked:
    {
      "detail": "Account locked due to KYC rejection"
    }

---

POST /auth/mfa/verify
Summary: Verificar código MFA y obtener tokens finales
Request Body (application/json):
  {
    "temp_token": "string (requerido, JWT de login con mfa_pending: true)",
    "code": "string (requerido, 6 dígitos, ej: 123456)"
  }

Responses:
  200 OK:
    {
      "access_token": "string (JWT con exp 30 min)",
      "refresh_token": "string (JWT con exp 7 días)",
      "token_type": "Bearer",
      "expires_in": 1800
    }
  
  401 Unauthorized (Invalid Code):
    {
      "detail": "Invalid MFA code",
      "attempts_remaining": 2
    }
  
  401 Unauthorized (Expired Temp Token):
    {
      "detail": "Temporary token expired, please login again"
    }
  
  429 Too Many Requests:
    {
      "detail": "Too many failed MFA attempts, please login again"
    }
```

DEINITION OF READY
1. ✅ Librería para manejo de JWT seleccionada: **PyJWT[crypto]** 2.10.1 (ver pyproject.toml).
2. ✅ Estructura de Claims y tiempos de expiración definidos (ver Acceptance Criteria #3).
3. ✅ Mock de MFA (código fijo "123456") acordado (ver Acceptance Criteria #2).
4. ✅ Estrategia de generación de claves RS256 definida (openssl rsa).

DEFINITION OF DONE (Global Policy):
1. **Formato:** Código formateado con **Black** e **Isort**.
2. **Linting:** Sin errores de **Ruff**.
3. **Typing:** **Mypy** en modo estricto pasando al 100%.
4. **Complejidad:** Complejidad Ciclomática < 10 por función.
5. **Cobertura de Pruebas:** >= 85% en líneas, statements, funciones y branches.
6. **Tipos de Tests:** Incluir casos positivos, negativos, edge cases, transiciones de estado, concurrencia y casos de integración (ver BACKEND-GUIDELINES.md sección 5.3.2).
7. **Docs:** Todos los métodos públicos documentados con **Google Docstrings**.
8. **Límites:** Ningún archivo excede las 500 líneas.
9. **Validación Local:** Ejecutar `black`, `isort`, `ruff`, `radon cc`, `mypy` y `pytest --cov` antes de commit.
10. Endpoints funcionales probados con Postman/httpx.
11. Test de integración que verifica flujo completo: Login → Token → MFA → Access Token.
12. Datos sensibles no expuestos en logs (passwords, hashes, tokens completos).
13. **JWT Security:** Validar firma, expiración y claims en cada endpoint protegido.


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