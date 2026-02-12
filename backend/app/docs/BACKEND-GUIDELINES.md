# Backend Guidelines – Auth & Users (Hexagonal Architecture)

## 1. Objetivo

Definir cómo estructurar y hacer evolucionar el microservicio de autenticación/usuarios usando arquitectura **hexagonal** en Python, alineado con:

- Requisitos de registro + KYC, autenticación segura y MFA.
- Atributos de calidad: seguridad, rendimiento, disponibilidad, escalabilidad, mantenibilidad.
- Evolución hacia microservicios (Auth, Users, Accounts, Transactions) detrás de un API Gateway.

Este documento debe ser fácilmente consumible tanto por un equipo de desarrollo como por un agente de IA.

---

## 2. Estructura de carpetas (vista general)

Raíz backend (ejemplo: `backend/`):

```text
backend/
  app/
    domain/
    application/
    adapters/
      inbound/
        http/
      outbound/
        db/
        kyc/
        security/
        messaging/
    config/
    shared/
  tests/
    unit/
    integration/
```

### 2.1. Dominio (`app/domain`)

Responsable de la lógica **de negocio pura** (sin dependencias de frameworks).

Subcarpetas sugeridas:

```text
app/domain/
  entities/
    user.py
    credential.py
    kyc_status.py
    mfa_config.py
  value_objects/
    phone_number.py
    document_id.py
    hashed_password.py
    jwt_token.py
  services/
    registration_service.py
    authentication_service.py
    mfa_service.py
  ports/
    user_repository.py
    kyc_verification_port.py
    password_hasher_port.py
    token_provider_port.py
    event_publisher_port.py
```

Principios:

- Solo tipos de dominio y **interfaces** (ports).
- No se importa nada de `FastAPI`, `SQLAlchemy`, ni librerías externas de infraestructura.

### 2.2. Capa de aplicación (`app/application`)

Orquesta casos de uso.

```text
app/application/
  use_cases/
    register_user_use_case.py
    login_user_use_case.py
    verify_mfa_use_case.py
    refresh_token_use_case.py
    lock_user_use_case.py
  dto/
    register_user_dto.py
    login_user_dto.py
    user_response_dto.py
```

Reglas:

- Cada caso de uso:
  - Expone un método `execute(input_dto) -> output_dto`.
  - Utiliza solo ports del dominio (no dependencias directas de adapters).
- Ningún acceso directo a HTTP, DB o librerías de seguridad.

### 2.3. Adapters de entrada (`app/adapters/inbound/http`)

Implementan la API REST (FastAPI).

```text
app/adapters/inbound/http/
  routers/
    auth_router.py
    users_router.py
  dependencies/
    container.py   # wiring de puertos ↔ implementaciones
```

Convenciones:

- Los routers:
  - Mapean `Request/Response` ⇄ DTOs de `application`.
  - No contienen lógica de negocio; llaman casos de uso.
- Definir versiones de API desde el inicio: `/api/v1/auth/login`, `/api/v1/auth/register`, etc.
- Preparar para convivir con API Gateway futuro (headers, JWT, correlation IDs).

### 2.4. Adapters de salida (`app/adapters/outbound`)

Implementan los ports del dominio.

```text
app/adapters/outbound/
  db/
    models.py        # SQLAlchemy
    user_repository_impl.py
  kyc/
    kyc_client_impl.py
  security/
    password_hasher_impl.py
    token_provider_impl.py
  messaging/
    event_publisher_inmemory.py
    # futuro: kafka_event_publisher_impl.py
```

Reglas:

- **DB (PostgreSQL)** alineada con UserDb de la arquitectura TO‑BE.
- `kyc_client_impl.py` inicialmente puede ser un mock HTTP que devuelve estados KYC válidos/ inválidos simulando proveedor KYC externo.
- `token_provider_impl.py` emite JWT con claims mínimos:
  - `sub` (user_id), `scope` (ej. `user`), `iat`, `exp`.
- `event_publisher_*`:
  - Para la PoC: implementación en memoria o log.
  - Futuro: publicación en Kafka/RabbitMQ como parte de la evolución a arquitectura orientada a eventos.

---

## 3. Patrones a aplicar en el backend

### 3.1. Arquitectura hexagonal (Ports & Adapters)

- **Ports** (interfaces) en `domain/ports`.
- **Adapters** en `adapters/*` que implementan esos ports.
- Dependencias:
  - `inbound adapters → application → domain → ports`
  - `outbound adapters → domain.ports` (implementan interfaces)
- Nunca al revés.

Beneficio: mantenibilidad y capacidad de evolución a microservicios, alineado con la refactorización de monolito a servicios especializados indicada en el TO‑BE.

### 3.2. Patrón Use Case (Application Service)

- Cada endpoint debe mapearse a un **caso de uso explícito**.
- Casos de uso coordinan:
  - Validación de DTOs.
  - Llamadas a servicios de dominio.
  - Interacción con repositorios / servicios externos a través de ports.
- Facilita pruebas unitarias aisladas y cumplimiento de atributos de calidad (mantenibilidad, testabilidad).

### 3.3. Patrón Repository

- `UserRepository` maneja todas las operaciones de persistencia de `User`.
- Implementación concreta (`user_repository_impl.py`) puede cambiar (PostgreSQL → otro) sin romper el dominio.

### 3.4. Patrón Anti‑Corrupción / Adaptador KYC

- `KycVerificationPort` protege al dominio de cambios de la API KYC externa.
- `kyc_client_impl.py` traduce DTOs internos a payloads externos.
- Permite cambiar de proveedor KYC sin impacto directo en dominio/casos de uso.

### 3.5. Patrón Event‑Driven (evolución futura)

- Definir desde hoy eventos de dominio:
  - `UserRegistered`, `UserKycApproved`, `UserLocked`, etc.
- `EventPublisherPort` y adapter minimalista (log/cola in‑memory) para la PoC.
- Evolución natural: publicar en un **Message Broker** (Kafka) alineado con la estrategia de microservicios y optimización de comunicación asíncrona.

---

## 4. Reglas de evolución

### 4.1. Añadir una nueva funcionalidad de dominio

Pasos estándar:

1. Definir la regla de negocio en `domain/services` o nueva entidad/value object.
2. Si se necesitan servicios externos o almacenamiento:
   - Crear/ajustar un **port** en `domain/ports`.
3. Crear o actualizar un **use case** en `application/use_cases`.
4. Implementar/actualizar el adapter correspondiente:
   - DB, KYC, security, messaging.
5. Añadir endpoint en `inbound/http/routers` que llame al use case.
6. Añadir pruebas unitarias de dominio y de caso de uso.

### 4.2. Extraer nuevos microservicios (futuro)

Cuando se introduzcan servicios como `AccountService` o `TransactionService` descritos en el TO‑BE:

- Reutilizar patrones:
  - Misma estructura `domain/application/adapters`.
- Comunicar servicios:
  - Sincronamente vía API Gateway (REST/gRPC).
  - Asíncronamente vía Event Bus (eventos de usuario, cuentas, movimientos).

---

## 5. Calidad, seguridad y observabilidad

### 5.1. Seguridad (alineada a QA‑001)

- Hashing de credenciales con Argon2/bcrypt.
- JWT con expiraciones cortas para access tokens y largos para refresh.
- MFA:
  - Capa de dominio define cuándo exigir MFA (ej. login desde dispositivo nuevo).
- Auditoría:
  - Registrar eventos clave: registro, intentos fallidos, cambios de KYC.

### 5.2. Rendimiento y escalabilidad

- Limitar lógica en endpoints; delegar a use cases.
- Preparar repositorio para **pagination** y filtros (consultas de usuarios).
- Exponer métricas (ej. con Prometheus) para futuras pruebas de carga, alineado con escenarios de calidad (QAS‑002, RNF‑002).

### 5.3. Testing

- **Unit tests**:
  - Dominio y casos de uso sin tocar DB ni HTTP.
- **Integration tests**:
  - Adapters de DB, KYC, security, messaging.
- Estructura:
  ```text
  tests/
    unit/
      domain/
      application/
    integration/
      adapters/
  ```

#### 5.3.1. Requisitos de cobertura y calidad

- **Cobertura mínima:** >= 85% en líneas, statements, funciones y branches para el scope del cambio (módulo/paquete afectado).
- **Complejidad ciclomática:** < 10 por función/método (verificar con análisis estático).
- **Tamaño de archivo:** Máximo 500 líneas por archivo (dividir/refactor si se excede).

#### 5.3.2. Tipos de tests obligatorios

Para cada funcionalidad nueva o modificada, incluir tests para:

1. **Casos positivos (happy path):**
   - Input válido produce output esperado
   - Ejemplo: registro con datos válidos → usuario creado exitosamente

2. **Casos negativos (error handling):**
   - Input inválido produce error apropiado
   - Ejemplo: registro con email duplicado → error 409 Conflict
   - Ejemplo: login con credenciales incorrectas → error 401 Unauthorized

3. **Edge cases (valores límite):**
   - Valores en los límites de validación
   - Ejemplo: contraseña de exactamente 8 caracteres (mínimo)
   - Ejemplo: username de 50 caracteres (máximo)
   - Ejemplo: listas vacías, strings vacíos, valores None/null

4. **Casos de estado (state transitions):**
   - Transiciones válidas e inválidas entre estados
   - Ejemplo: usuario "pending_kyc" → "active" (válido)
   - Ejemplo: usuario "locked" → "active" sin unlock (inválido)

5. **Casos de concurrencia (cuando aplique):**
   - Múltiples operaciones simultáneas
   - Ejemplo: dos registros simultáneos con mismo email

6. **Casos de integración:**
   - Interacción con sistemas externos
   - Ejemplo: KYC service devuelve timeout → manejo apropiado
   - Ejemplo: DB connection falla → retry y error handling

#### 5.3.3. Estructura de tests (ejemplos)

**Unit test - Caso de uso:**
```python
def test_register_user_when_valid_data_then_user_created():
    # Arrange
    mock_repo = Mock(spec=UserRepository)
    mock_kyc = Mock(spec=KycVerificationPort)
    mock_hasher = Mock(spec=PasswordHasherPort)
    mock_hasher.hash_password.return_value = "hashed_password"
    use_case = RegisterUserUseCase(mock_repo, mock_kyc, mock_hasher)
    input_dto = RegisterUserDTO(email="test@example.com", password="Pass123!")
    
    # Act
    result = use_case.execute(input_dto)
    
    # Assert
    assert result.success is True
    mock_repo.save.assert_called_once()

def test_register_user_when_duplicate_email_then_raises_conflict():
    # Arrange
    mock_repo = Mock(spec=UserRepository)
    mock_repo.find_by_email.return_value = User(email="test@example.com")
    use_case = RegisterUserUseCase(mock_repo, None, None)
    input_dto = RegisterUserDTO(email="test@example.com", password="Pass123!")
    
    # Act & Assert
    with pytest.raises(ConflictError, match="Email already exists"):
        use_case.execute(input_dto)
```

**Integration test - Repository:**
```python
@pytest.mark.asyncio
async def test_user_repository_save_when_valid_user_then_persisted():
    # Arrange
    db_client = await get_test_db_client()
    repo = UserRepositoryImpl(db_client)
    user = User(email="test@example.com", password_hash="hashed")
    
    # Act
    saved_user = await repo.save(user)
    
    # Assert
    assert saved_user.id is not None
    found_user = await repo.find_by_id(saved_user.id)
    assert found_user.email == "test@example.com"
    
    # Cleanup
    await db_client.users.delete_many({"email": "test@example.com"})
```

#### 5.3.4. Validación antes de commit

Ejecutar **siempre** antes de crear PR:
```bash
# Formato
black app/
isort app/

# Linting
ruff check app/

# Type checking
mypy app/

# Tests con cobertura
pytest --cov=app --cov-report=term --cov-report=html

# Verificar que todos pasen sin errores
```

### 5.4. Patrón AAA (Arrange‑Act‑Assert) para tests

- **Regla:** Todos los tests (unitarios e integraciones) deben seguir el patrón **AAA**: _Arrange_ (preparar datos/fixtures/mocks), _Act_ (ejecutar la unidad bajo prueba) y _Assert_ (verificar resultados).
- **Unit tests:** Mantenerlos pequeños y deterministas; hacer `Arrange` con objetos/ports simulados, `Act` llamando al caso de uso/servicio, `Assert` sobre el DTO/estado devuelto.
- **Integration tests:** Separar claramente la preparación del entorno (DB, cliente KYC simulado, proveedores de seguridad), ejecutar el flujo completo y limpiar recursos en el `teardown`.
- **Convenciones:** Usar nombres descriptivos (`test_<unit>_when_<condition>_then_<expected>`), helpers/fixtures para `Arrange`, y comentarios `// Arrange // Act // Assert` si ayuda a la legibilidad.

---

## 6. Convenciones para agentes de IA

- Arquitectura siempre referenciada como **“hexagonal (ports & adapters)”**.
- Casos de uso deben describirse explícitamente con:
  - `input_dto`, `output_dto`, puertos que utiliza.
- Nuevos accesos a sistemas externos:
  - Crear primero un **port**.
  - Luego un adapter en `adapters/outbound`.
- Mantener esta guía actualizada cuando:
  - Se definan nuevos servicios (Accounts, Transactions).
  - Cambie la política de seguridad (nuevos campos JWT, flujos MFA).