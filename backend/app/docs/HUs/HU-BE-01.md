SYSTEM INSTRUCTION:
Actúa como un Desarrollador Backend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-BE-01
Work Item Type: User Story
Title: Implementar endpoint de registro y almacenamiento en Colección de Usuarios
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\BackEnd
Iteration: PoC\Sprint 1
Tags: [Python, FastAPI, MongoDB, Hexagonal, Auth]

DESCRIPTION:
Como **Arquitecto de Solución**,
Quiero **un endpoint de registro que guarde la información del usuario en MongoDB tras validar reglas de negocio**,
Para **permitir el alta de usuarios cumpliendo los requisitos de identidad y unicidad.**

ACCEPTANCE CRITERIA:
1.  **Modelo de Datos:** Documento JSON en colección `users` con los siguientes campos:
    - `phone`: Número de teléfono en formato internacional (ej: +573001234567). Debe tener un índice único que se crea automáticamente al inicio de la aplicación si no existe.
    - `email`: Correo electrónico (opcional, máximo 255 caracteres).
    - `password_hash`: Hash de la contraseña usando Argon2.
    - `kyc_status`: Estado de verificación KYC (valores posibles: "pending", "approved", "rejected").
    - `mfa_enabled`: Indica si MFA está habilitado (boolean, inicialmente `false`).
    - `created_at`: Fecha y hora de creación del usuario.

2.  **Validación de Contraseña:** La contraseña recibida debe cumplir:
    - Mínimo 8 caracteres, máximo 128 caracteres.
    - Al menos una letra mayúscula, una minúscula, un número y un carácter especial.
    - Retornar `422 Unprocessable Entity` si no cumple las reglas.

3.  **Seguridad:** La contraseña nunca se guarda en texto plano; usar **Argon2** para generar el hash.

4.  **Mock KYC:** El servicio debe llamar a una función interna simulada de verificación KYC:
    - Si el teléfono termina en **"00"** (ej: +573001234500), el mock rechaza la verificación → `kyc_status: "rejected"` y el usuario NO se crea.
    - Si el teléfono termina en **"99"** (ej: +573001234599), el mock aprueba inmediatamente → `kyc_status: "approved"`.
    - Para cualquier otro teléfono, el mock deja pendiente la verificación → `kyc_status: "pending"`.

5.  **Manejo de Errores:** 
    - Retornar `409 Conflict` si el teléfono ya existe.
    - Retornar `422 Unprocessable Entity` si la validación de campos falla.
    - Retornar `400 Bad Request` si el KYC rechaza al usuario.

6.  **Respuesta Exitosa:** `201 Created` retornando únicamente el `user_id` generado.

7.  **Contrato OpenAPI:** El endpoint debe cumplir con el siguiente contrato:

```yaml
POST /auth/register
Summary: Registrar un nuevo usuario
Request Body (application/json):
  {
    "phone": "string (requerido, formato E.164: +[código_país][número])",
    "password": "string (requerido, 8-128 caracteres con mayúsculas, minúsculas, números y especiales)",
    "email": "string (opcional, máximo 255 caracteres, formato email válido)",
    "name": "string (opcional, máximo 100 caracteres)"
  }

Responses:
  201 Created:
    {
      "user_id": "string (ID generado del usuario, ej: 507f1f77bcf86cd799439011)"
    }
  
  400 Bad Request:
    {
      "detail": "KYC verification rejected for this phone number"
    }
  
  409 Conflict:
    {
      "detail": "Phone number already registered"
    }
  
  422 Unprocessable Entity:
    {
      "detail": [
        {
          "loc": ["body", "password"],
          "msg": "Password must contain at least one uppercase letter",
          "type": "value_error"
        }
      ]
    }
```

DEINITION OF READY
1. ✅ Contrato de interfaz (Swagger/OpenAPI) para `POST /auth/register` definido y aprobado (ver Acceptance Criteria #7).
2. ✅ Reglas de validación de contraseña y teléfono definidas (ver Acceptance Criteria #1 y #2).
3. ✅ Mock del servicio KYC (simulado) acordado (ver Acceptance Criteria #4).

DEFINITION OF DONE (Global Policy):
1. **Formato:** Código formateado con **Black** e **Isort**.
2. **Linting:** Sin errores de **Ruff**.
3. **Typing:** **Mypy** en modo estricto pasando al 100%.
4. **Complejidad:** Complejidad Ciclomática < 10 por función.
5. **Cobertura de Pruebas:** >= 85% en líneas, statements, funciones y branches.
6. **Tipos de Tests:** Incluir casos positivos, negativos, edge cases, transiciones de estado y casos de integración (ver BACKEND-GUIDELINES.md sección 5.3.2).
7. **Docs:** Todos los métodos públicos documentados con **Google Docstrings**.
8. **Límites:** Ningún archivo excede las 500 líneas.
9. **Validación Local:** Ejecutar `black`, `isort`, `ruff`, `radon`, `mypy` y `pytest --cov` antes de commit.
10. Endpoint funcional probado con Postman/httpx.
11. Test de integración que verifica la inserción real en MongoDB.
12. Datos sensibles no expuestos en logs (passwords, hashes, tokens).


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