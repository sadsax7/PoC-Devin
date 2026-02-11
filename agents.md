# agents.md — Instrucciones para agentes (Billetera Virtual)

Este documento define cómo deben operar los agentes de IA que contribuyen al repositorio de la **Billetera Virtual**.
El objetivo es que cada entrega sea consistente con el stack, la arquitectura y los controles automáticos de calidad del proyecto.

## 0) Documentos de referencia obligatorios

Antes de diseñar o implementar, el agente debe consultar:

- `BACKEND-GUIDELINES.md`: convenciones, arquitectura, estructura de carpetas, estándares de API, seguridad, observabilidad y prácticas backend.
- `FRONTEND-GUIDELINES.md`: convenciones de UI, Atomic Design, estilos/tema, manejo de estado, consumo de API, accesibilidad, y estándares frontend.

### Precedencia (cuando hay conflictos)
- **Work Items (Azure DevOps)** definen el **WHAT**: alcance, reglas de negocio, criterios de aceptación y DoD/DoR.
- `BACKEND-GUIDELINES.md` / `FRONTEND-GUIDELINES.md` definen el **HOW**: patrones, convenciones y decisiones técnicas estándar del proyecto.
- Si el Work Item contradice una guideline (ej. pide romper una regla de seguridad o calidad), el agente debe **detenerse y preguntar** (ver sección 10) antes de codificar.

## 1) Fuente de verdad: Azure DevOps Work Items

La fuente de verdad funcional y técnica es **siempre** el Work Item asignado (User Story / Task / Bug) en Azure DevOps, incluyendo:
- ID, Title, State, Assigned To
- Area Path, Iteration, Tags
- Description
- Acceptance Criteria
- Definition of Ready (DoR)
- Definition of Done (DoD)

Reglas:
- No implementar funcionalidades “extra” no solicitadas en el Work Item.
- Si el Work Item es ambiguo o contradictorio, detener implementación y preguntar (ver sección 10).
- Si se requiere refactor grande, proponerlo como Work Item nuevo en lugar de “colarlo” en el PR.

## 2) Arquitectura y organización del código

### 2.1 Backend — Python / FastAPI / Hexagonal / MongoDB (Motor)
- Arquitectura Hexagonal (Ports & Adapters):
  - `app/domain/`: entidades, value objects, servicios de dominio, puertos (interfaces).
  - `app/application/`: casos de uso, DTOs de entrada/salida.
  - `app/infrastructure/adapters/inbound/http/`: routers FastAPI, mapeado Request/Response ↔ DTOs.
  - `app/infrastructure/adapters/outbound/`: implementaciones de puertos (DB, KYC, security, messaging).
  - `app/config/`: configuración y wiring.
  - `app/shared/`: utilidades compartidas.
- Principio clave: el **dominio no depende** de FastAPI, Motor u otros detalles de infraestructura.
- MongoDB se accede con **Motor** (async) y la infraestructura encapsula el driver.
- Stack de dependencias:
  - **FastAPI** (>=0.128.0): framework web async.
  - **Motor** (>=3.7.1): driver async para MongoDB.
  - **Pydantic** (>=2.12.5): validación de DTOs.
  - **PyJWT[crypto]** (>=2.10.1): manejo de tokens JWT.
  - **Argon2-cffi** (>=25.1.0): hashing de contraseñas.
  - **Httpx** (>=0.28.1): cliente HTTP async para integraciones externas.

### 2.2 Frontend — Next.js / TypeScript / Atomic Design
- Atomic Design:
  - `src/components/atoms/`: componentes básicos sin lógica de negocio (Button, TextField, etc).
  - `src/components/molecules/`: agrupaciones simples de átomos (FormField, OtpCodeInput, etc).
  - `src/components/organisms/`: estructuras funcionales (LoginForm, RegisterForm, etc).
  - `src/components/templates/`: layouts de páginas (AuthPageTemplate, DashboardTemplate, etc).
  - `src/app/`: rutas Next.js (App Router) que ensamblan templates y organisms.
- Capa de acceso:
  - `src/lib/api/`: cliente HTTP (axios/fetch wrapper) y funciones de API.
  - `src/lib/auth/`: hooks de casos de uso UI (useLogin, useRegister, useMfa, etc) y contexto.
- Principio clave: las páginas solo ensamblan, la lógica vive en hooks (`lib/`) y organisms.
- Stack de dependencias:
  - **Next.js** (16.1.6): framework React con App Router.
  - **React** (19.2.3): librería UI.
  - **TypeScript** (^5.9.3): tipado estático.
  - **TailwindCSS** (^4): sistema de diseño utility-first.

## 3) Políticas globales de calidad (bloqueantes)

Estas reglas aplican a **toda** entrega (nuevo código o cambios).

### 3.1 Métricas obligatorias
- Complejidad ciclomática: **< 10** por función/método.
- Cobertura de pruebas unitarias: **>= 85%** para el alcance del cambio (módulo/paquete afectado).
- Tamaño de archivo: máximo **500 líneas por archivo** (si se excede, dividir/refactor).
- Documentación:
  - Backend: **Google Docstrings** (módulos, clases y funciones públicas).
  - Frontend: **TSDoc** (componentes/hooks/funciones públicas y tipos exportados).

### 3.2 Backend — herramientas oficiales del repo
- Formato: **Black** (>=26.1.0) + **isort** (>=7.0.0)
- Linting: **Ruff** (>=0.14.14)
- Typing: **MyPy** (>=1.19.1)
- Complejidad: Verificar con análisis estático **Radon** (umbral < 10 por función/método)
- Tests: **PyTest** (>=9.0.2) + **pytest-asyncio** (>=1.3.0) + **pytest-cov** (>=7.0.0)
- Pre-commit hooks: **pre-commit** (>=4.5.1) para validación automática

### 3.3 Frontend — herramientas oficiales del repo
- Linting: **ESLint** (^9) con plugins:
  - **eslint-config-next** (16.1.6): reglas específicas de Next.js.
  - **eslint-config-prettier** (^10.1.8): integración con Prettier.
  - **eslint-plugin-sonarjs** (^3.0.6): reglas de calidad de código.
  - **eslint-plugin-tsdoc** (^0.5.0): validación de documentación TSDoc.
  - **eslint-plugin-unused-imports** (^4.3.0): detección de imports no usados.
- Formato: **Prettier** (^3.8.1)
- Typing: **TypeScript** (^5.9.3) con `tsconfig.json` estricto
- Tests unitarios: **Mocha** (^11.3.0) + **Chai** (^6.2.2) + **Sinon** (^21.0.1)
- Coverage: **nyc** (^17.1.0)
- Environment de pruebas: **jsdom** (^27.4.0) para simular DOM
- El agente debe seguir la convención de nombres, ubicación de tests y scripts de `package.json`.

## 4) Estándares de implementación (prácticos)

- Mantener cambios mínimos y enfocados en el Work Item.
- Favorecer funciones pequeñas, con responsabilidades claras (ayuda a complejidad < 10).
- Validar inputs en el borde (controller/handler), y reglas de negocio en `domain`/`application`.
- Errores deben ser consistentes y testeables; evitar prints/logs con datos sensibles.

## 5) Estándares específicos de implementación

### 5.1 Backend — Patrones obligatorios

#### 5.1.1 Arquitectura Hexagonal (Ports & Adapters)
- **Flujo de dependencias**: `inbound adapters → application → domain → ports`
- **Adapters de salida**: implementan `domain.ports` sin que el dominio los conozca.
- **Nunca**: hacer que el dominio dependa de FastAPI, Motor, librerías externas.

#### 5.1.2 Patrón Use Case (Application Service)
- Cada endpoint debe mapearse a un **caso de uso explícito** en `app/application/use_cases/`.
- Firma estándar: `execute(input_dto: InputDTO) -> OutputDTO`.
- El caso de uso coordina:
  - Validación de DTOs (Pydantic).
  - Llamadas a servicios de dominio.
  - Interacción con repositorios/servicios externos vía ports.

#### 5.1.3 Patrón Repository
- Todos los accesos a persistencia (MongoDB/Motor) deben encapsularse en repositorios.
- Interfaz (port) en `app/domain/ports/` (ej. `UserRepository`).
- Implementación en `app/adapters/outbound/db/` (ej. `UserRepositoryImpl`).

#### 5.1.4 Patrón Anti-Corrupción (KYC y servicios externos)
- Definir port en `app/domain/ports/` (ej. `KycVerificationPort`).
- Implementar adapter en `app/adapters/outbound/kyc/` que traduzca DTOs internos ↔ payloads externos.
- Beneficio: cambiar proveedor sin impactar dominio.

#### 5.1.5 Event-Driven (preparación futura)
- Definir eventos de dominio: `UserRegistered`, `UserKycApproved`, `UserLocked`, etc.
- Port: `EventPublisherPort` en `app/domain/ports/`.
- Adapter minimalista (log/in-memory) para PoC en `app/adapters/outbound/messaging/`.
- Evolución: publicar en Kafka/RabbitMQ cuando se requiera comunicación asíncrona entre microservicios.

#### 5.1.6 Seguridad
- Hashing: **Argon2** (argon2-cffi) para contraseñas.
- JWT: **PyJWT[crypto]** con expiraciones cortas (access) y largas (refresh).
- MFA: lógica en `app/domain/services/mfa_service.py`, decisión de cuándo exigir MFA en dominio.
- Auditoría: registrar eventos clave en logs estructurados (sin PII/secretos).

#### 5.1.7 Testing Backend
- **Unit tests** (`tests/unit/`):
  - Dominio y casos de uso sin tocar DB ni HTTP.
  - Usar mocks/stubs para ports.
  - Patrón AAA obligatorio.
  - **OBLIGATORIO**: Incluir casos positivos, negativos y edge cases (ver 5.1.7.1).
- **Integration tests** (`tests/integration/`):
  - Adapters de DB, KYC, security, messaging.
  - Usar fixtures para preparar entorno.
  - Limpiar recursos en `teardown`.
  - **OBLIGATORIO**: Incluir casos de error, timeout y concurrencia.
- Nombres descriptivos: `test_<unit>_when_<condition>_then_<expected>`.
- **Cobertura mínima**: >= 85% en el scope del cambio.

##### 5.1.7.1 Tipos de tests obligatorios (Backend)

Para **CADA** funcionalidad nueva o modificada, el agente DEBE implementar tests para:

1. **Casos positivos (happy path)**:
   - Input válido → output esperado
   - Ejemplo: `test_register_user_when_valid_data_then_user_created()`
   - Ejemplo: `test_login_when_correct_credentials_then_token_returned()`

2. **Casos negativos (error handling)**:
   - Input inválido → error apropiado
   - Ejemplo: `test_register_user_when_duplicate_email_then_raises_conflict()`
   - Ejemplo: `test_login_when_wrong_password_then_raises_unauthorized()`
   - Ejemplo: `test_kyc_verify_when_service_unavailable_then_raises_service_error()`

3. **Edge cases (valores límite)**:
   - Valores en límites de validación
   - Ejemplo: `test_register_user_when_password_min_length_then_accepted()`
   - Ejemplo: `test_register_user_when_password_too_short_then_rejected()`
   - Ejemplo: `test_get_users_when_empty_db_then_returns_empty_list()`
   - Ejemplo: `test_update_user_when_none_values_then_handles_gracefully()`

4. **Casos de estado (state transitions)**:
   - Transiciones válidas e inválidas
   - Ejemplo: `test_user_when_pending_kyc_to_active_then_succeeds()`
   - Ejemplo: `test_user_when_locked_to_active_without_unlock_then_fails()`

5. **Casos de integración (integration tests)**:
   - Interacción con sistemas externos
   - Ejemplo: `test_kyc_adapter_when_timeout_then_retries_and_fails()`
   - Ejemplo: `test_repository_when_db_connection_lost_then_raises_error()`

**Ejemplo completo de cobertura para `RegisterUserUseCase`**:
```python
# 1. Caso positivo
def test_register_user_when_valid_data_then_user_created(): ...

# 2. Casos negativos
def test_register_user_when_duplicate_email_then_raises_conflict(): ...
def test_register_user_when_invalid_email_format_then_raises_validation_error(): ...
def test_register_user_when_weak_password_then_raises_validation_error(): ...

# 3. Edge cases
def test_register_user_when_password_exactly_min_length_then_accepted(): ...
def test_register_user_when_email_max_length_then_accepted(): ...
def test_register_user_when_empty_phone_then_accepted(): ...

# 4. Casos de estado
def test_register_user_when_kyc_pending_then_status_is_pending(): ...

# 5. Integración
def test_register_user_when_kyc_service_down_then_raises_service_error(): ...
```

**NO ACEPTABLE**: Tests que solo cubren el happy path sin casos negativos ni edge cases.

### 5.2 Frontend — Patrones obligatorios

#### 5.2.1 Atomic Design (organización de componentes)
- **Atoms** (`src/components/atoms/`):
  - Componentes básicos sin lógica de negocio: Button, TextField, Icon, etc.
  - Solo reciben props y emiten eventos.
- **Molecules** (`src/components/molecules/`):
  - Agrupaciones de átomos: FormField (label + input + error), OtpCodeInput, etc.
  - Validaciones ligeras de UI.
- **Organisms** (`src/components/organisms/`):
  - Estructuras funcionales: LoginForm, RegisterForm, MfaForm, etc.
  - Manejan estado local de formulario.
  - Invocan hooks de `lib/`.
- **Templates** (`src/components/templates/`):
  - Layouts de páginas: AuthPageTemplate, DashboardTemplate, etc.
  - Reciben organisms como children.
  - Sin lógica de negocio.
- **Pages** (`src/app/...`):
  - Rutas Next.js que ensamblan templates y organisms.
  - Conectan con router/metadata.
  - Sin lógica de negocio repetida.

#### 5.2.2 Pattern: UI Use Case Hook
- Para cada "capacidad" de UI, crear hook dedicado en `lib/`:
  - `src/lib/auth/useLogin.ts`
  - `src/lib/auth/useRegister.ts`
  - `src/lib/auth/useMfa.ts`
  - etc.
- Cada hook:
  - Llama a `lib/api/` (cliente HTTP).
  - Maneja `isLoading`, `error`, `data`.
  - Expone funciones y estado al organism.
- Beneficio: organisms desconocen detalles de API, facilita testing y localización de cambios.

#### 5.2.3 Pattern: Thin Page, Rich Template/Organism
- Las páginas (Next.js) solo ensamblan:
  - Template adecuado.
  - Organisms necesarios.
- La lógica de negocio de UI vive en:
  - Hooks (`lib/`) y organisms.
- Evitar componentes "Dios": preferir composición.

#### 5.2.4 Cliente HTTP (`src/lib/api/`)
- `client.ts`: wrapper de axios/fetch con:
  - `baseURL` del backend.
  - Interceptores para adjuntar `Authorization: Bearer <token>`.
  - Manejo de 401/403 (refresco de token, redirección).
- `auth_api.ts`: funciones específicas (`login()`, `register()`, `verifyMfa()`, `getProfile()`).
- Nunca hardcodear tokens o secretos.

#### 5.2.5 Manejo de estado de autenticación
- `src/lib/auth/auth_context.tsx`:
  - Almacena usuario actual y access token en memoria.
  - Integra refresh token vía cookie httpOnly (backend).
- Hooks de auth consumen este contexto.

#### 5.2.6 Design Tokens & Theming
- Definir en `src/styles/` o `src/config/theme.ts`:
  - Colores, tipografía, espaciados, border radius.
- Usar TailwindCSS (^4) con configuración centralizada.
- Todos los átomos deben usar tokens, no valores hardcodeados.
- Facilita consistencia UX web/móvil.

#### 5.2.7 Testing Frontend
- **Unit tests**:
  - Átomos y moléculas: render, props.
  - Organisms: simular inputs, verificar llamadas a hooks.
  - Usar Mocha + Chai + Sinon.
  - Patrón AAA obligatorio.
  - **OBLIGATORIO**: Incluir casos positivos, negativos, edge cases, interacciones y accesibilidad (ver 5.2.7.1).
- **Integration tests**:
  - Flujos críticos: registro + login + MFA.
  - Mock de API con Sinon.
  - Usar jsdom para simular DOM.
  - **OBLIGATORIO**: Incluir casos de error de red, timeout y transiciones de estado.
- Nombres descriptivos: `should_render_with_default_props_when_disabled`.
- Cobertura con nyc >= 85%.

##### 5.2.7.1 Tipos de tests obligatorios (Frontend)

Para **CADA** componente/hook nuevo o modificado, el agente DEBE implementar tests para:

1. **Casos positivos (happy path)**:
   - Render con props válidas produce output esperado
   - Ejemplo: `should_render_button_with_text_when_children_provided()`
   - Ejemplo: `should_return_token_when_login_succeeds()`

2. **Casos negativos (error handling)**:
   - Props inválidas o errores de API
   - Ejemplo: `should_not_crash_when_children_is_null()`
   - Ejemplo: `should_show_error_message_when_login_fails_401()`
   - Ejemplo: `should_handle_network_error_gracefully()`

3. **Edge cases (valores límite)**:
   - Props en los límites de validación
   - Ejemplo: `should_truncate_text_when_max_length_exceeded()`
   - Ejemplo: `should_render_empty_state_when_list_is_empty()`
   - Ejemplo: `should_handle_undefined_props_gracefully()`

4. **Casos de interacción (user interactions)**:
   - Eventos de usuario
   - Ejemplo: `should_call_onClick_handler_when_button_clicked()`
   - Ejemplo: `should_update_state_when_input_changes()`
   - Ejemplo: `should_show_loading_when_form_submits()`

5. **Casos de estado (state transitions)**:
   - Transiciones entre estados del componente
   - Ejemplo: `should_transition_from_idle_to_loading_to_success()`
   - Ejemplo: `should_transition_to_error_state_when_api_fails()`

6. **Casos de accesibilidad**:
   - ARIA labels, roles, keyboard navigation
   - Ejemplo: `should_have_aria_label_when_icon_only_button()`
   - Ejemplo: `should_associate_label_with_input_via_htmlFor()`
   - Ejemplo: `should_announce_error_with_aria_live()`

7. **Casos de props variations**:
   - Diferentes combinaciones de props
   - Ejemplo: `should_render_as_primary_when_variant_is_primary()`
   - Ejemplo: `should_disable_button_when_disabled_is_true()`
   - Ejemplo: `should_apply_custom_className_alongside_default_classes()`

**Ejemplo completo de cobertura para `LoginForm`**:
```tsx
// 1. Caso positivo
should_render_email_and_password_fields()

// 2. Casos negativos
should_show_error_when_credentials_invalid()
should_handle_network_error_gracefully()

// 3. Edge cases
should_not_crash_when_onLogin_is_undefined()
should_disable_submit_when_fields_empty()

// 4. Interacciones
should_call_onLogin_when_form_submits()
should_update_email_state_when_input_changes()

// 5. Estados
should_show_loading_spinner_when_submitting()
should_transition_from_loading_to_error_state()

// 6. Accesibilidad
should_have_labels_for_all_inputs()
should_announce_errors_with_aria_live()

// 7. Props variations
should_render_with_custom_button_text()
should_disable_form_when_disabled_prop_true()
```

**NO ACEPTABLE**: 
- Tests que solo verifican render básico sin casos de error
- Tests que ignoran interacciones de usuario
- Tests sin validación de accesibilidad en componentes interactivos
- Tests que no cubren edge cases como props undefined/null

## 6) Seguridad y manejo de datos sensibles

- Prohibido hardcodear secretos (tokens, passwords, connection strings, API keys).
- `.env` real nunca se commitea; usar `.env.example` si aplica.
- Logs: no imprimir PII o secretos (passwords, hashes, tokens, códigos MFA).
- Respuestas de API: nunca retornar `password_hash` u otros secretos.
- Backend: usar variables de entorno con validación Pydantic.
- Frontend: solo variables públicas `NEXT_PUBLIC_*` en cliente, secretos en servidor.

## 7) Flujo de entrega por Work Item (obligatorio)

Para cada Work Item, el agente debe producir:

1. **Análisis breve**
- Interpretación de Description + Acceptance Criteria + DoD.
- Lista de archivos a tocar y por qué.
- Confirmar alineación con `BACKEND-GUIDELINES.md` o `FRONTEND-GUIDELINES.md` según aplique.
- Identificar capa afectada: Backend (dominio/application/adapters) o Frontend (atoms/molecules/organisms/lib).

2. **Implementación**
- Código que cumple Acceptance Criteria.
- Respetar arquitectura y límites (500 líneas, complejidad < 10).
- Backend: seguir patrones de sección 5.1.
- Frontend: seguir patrones de sección 5.2.

3. **Pruebas**
- Unit tests para lógica nueva o modificada (patrón AAA obligatorio).
- Casos positivos, negativos y edge cases relevantes.
- Backend: tests de dominio + casos de uso + adapters.
- Frontend: tests de componentes + hooks + flujos críticos.

4. **Verificación local**
- Ejecutar las herramientas de calidad configuradas en el repo:
  - Backend: `black`, `isort`, `ruff`, `mypy`, `pytest`, `pytest --cov`.
  - Frontend: `npm run lint`, `npx prettier --check`, `tsc --noEmit`, `npm test`, `nyc npm test`.

5. **Documentación**
- Backend: Google Docstrings en módulos, clases y funciones públicas.
- Frontend: TSDoc en componentes, hooks y funciones públicas.
- Actualizar README/guías si el cambio introduce un patrón nuevo.

## 8) Checklist DoD (para cada PR)

El PR solo se considera listo para review si cumple **todos** los criterios aplicables según la capa (Backend/Frontend):

### 8.1 Backend (Python / FastAPI)
- [ ] **Black** (>=26.1.0): formato aplicado (`black app/`).
- [ ] **isort** (>=7.0.0): imports ordenados (`isort app/`).
- [ ] **Ruff** (>=0.14.14): linting pasa sin errores (`ruff check app/`).
- [ ] **MyPy** (>=1.19.1): typing pasa sin errores (`mypy app/`).
- [ ] **Complejidad ciclomática**: < 10 por función/método (verificar con análisis estático).
- [ ] **PyTest** (>=9.0.2): todos los tests pasan (`pytest`).
- [ ] **Cobertura**: >= 85% en el scope del cambio (`pytest --cov=app --cov-report=term`).
- [ ] **Tamaño de archivo**: ningún archivo supera 500 líneas.
- [ ] **Google Docstrings**: módulos, clases y funciones públicas documentadas.
- [ ] **Arquitectura Hexagonal**: dominio no depende de infraestructura.
- [ ] **Tests con patrón AAA**: Arrange-Act-Assert en todos los tests.
- [ ] **Seguridad**: sin secretos hardcodeados, sin PII en logs.
- [ ] **Pre-commit hooks**: validación automática configurada.

### 8.2 Frontend (Next.js / TypeScript)
- [ ] **ESLint** (^9): linting pasa sin errores (`npm run lint`).
- [ ] **Prettier** (^3.8.1): formato aplicado (`npx prettier --check .`).
- [ ] **TypeScript** (^5.9.3): compilación sin errores (`tsc --noEmit`).
- [ ] **Mocha** (^11.3.0): todos los tests pasan (`npm test`).
- [ ] **Cobertura**: >= 85% en el scope del cambio (`nyc npm test`).
- [ ] **Tamaño de archivo**: ningún archivo supera 500 líneas.
- [ ] **TSDoc**: componentes, hooks y funciones públicas documentadas.
- [ ] **Atomic Design**: componentes en la capa correcta (atoms/molecules/organisms/templates).
- [ ] **Tests con patrón AAA**: Arrange-Act-Assert en todos los tests.
- [ ] **UI Use Case Hook**: lógica de negocio en hooks de `lib/`, no en componentes.
- [ ] **Seguridad**: sin secretos hardcodeados, tokens en memoria/cookies httpOnly.
- [ ] **Accesibilidad**: formularios con labels, ARIA cuando sea necesario.

### 8.3 Común (Backend y Frontend)
- [ ] Se siguieron las convenciones de `BACKEND-GUIDELINES.md` / `FRONTEND-GUIDELINES.md`.
- [ ] No se introducen secretos ni exposición de datos sensibles.
- [ ] Ningún archivo supera 500 líneas (dividir/refactor si es necesario).
- [ ] Cobertura >= 85% (en el scope del cambio).
- [ ] Tests siguen el patrón AAA (Arrange-Act-Assert).
- [ ] Commit message sigue convención: `[<WORK_ITEM_ID>] <Descripción corta>`.

## 9) Estándar de Pull Request (PR)

**Título**
- `[<WORK_ITEM_ID>] <Descripción corta>`
  - Ej: `[HU-BE-02] Login con JWT y verificación MFA`
  - Ej: `[HU-FE-03] LoginForm con validación y manejo de errores`

**Descripción**
- Qué se implementó (bullets).
- Cómo probar (pasos + comandos específicos).
- Evidencia de métricas:
  - **Backend**: Coverage alcanzada (>=85%), Typing (MyPy ok), Lint (Ruff ok), Límite de líneas (<=500), Complejidad (< 10).
  - **Frontend**: Coverage alcanzada (>=85%), TypeScript ok, ESLint ok, Límite de líneas (<=500).
- Referencia explícita si se siguió un patrón tomado de `BACKEND-GUIDELINES.md` / `FRONTEND-GUIDELINES.md`.
- Capturas de pantalla o GIFs si es cambio de UI.

## 10) Regla de refactor

- Refactorizar solo si:
  - Es necesario para cumplir el Work Item, o
  - Es necesario para cumplir métricas (complejidad < 10, tamaño <= 500 líneas, cobertura >= 85%, testabilidad).
- Refactors grandes deben proponerse como Work Item nuevo.
- Mantener alcance mínimo: no "colar" mejoras no relacionadas.

## 11) Protocolo de preguntas (cuando falta contexto)

Si hay ambigüedad, el agente debe preguntar antes de codificar.

Formato:
- Pregunta (1 línea).
- Contexto (qué parte del Work Item/repo/guidelines genera la duda).
- Opciones (A/B) con trade-offs.
- Recomendación (qué elegiría el agente).
- Bloqueo (qué no puede terminar sin respuesta).
