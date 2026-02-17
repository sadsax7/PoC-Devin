# Frontend Guidelines – Web App (Atomic Design + Next.js)

## 1. Objetivo

Definir cómo estructurar y hacer evolucionar la interfaz web usando **Atomic Design** sobre React 18 + Next.js, alineado con:

- Interfaz Web complementaria con funcionalidades clave (registro, login, perfil).
- Atributos de calidad: usabilidad, consistencia UX en web/móvil, rendimiento y mantenibilidad.

Esta guía debe ser entendible por equipo de frontend y agentes de IA.

---

## 2. Estructura de carpetas (Next.js + Atomic Design)

Ejemplo con Next.js App Router:

```text
frontend/
  src/
    app/
      auth/
        login/
        register/
        mfa/
      profile/
      layout.tsx
      page.tsx
    components/
      atoms/
      molecules/
      organisms/
      templates/
    lib/
      api/
      auth/
    styles/
    config/
```

Si se usa Pages Router, adaptar a `pages/` manteniendo la misma idea de `components/*`.

---

## 3. Atomic Design

### 3.1. Atoms (`components/atoms`)

Componentes más básicos, sin conocimiento de dominio.

Ejemplos:

- `Button`, `TextField`, `PasswordField`, `PhoneInput`.
- `Checkbox`, `Radio`, `Label`.
- `Alert`, `Spinner`, `Icon`, `Typography`.

Reglas:

- No contienen lógica de negocio ni llamadas a API.
- Solo reciben props y emiten eventos (ej. `onClick`, `onChange`).

### 3.2. Molecules (`components/molecules`)

Agrupan átomos para roles simples.

Ejemplos:

- `FormField` (label + input + error).
- `OtpCodeInput` (conjunto de 6 inputs).
- `NavbarItem`, `UserAvatar`, `KeyValueRow`.

Reglas:

- Pueden contener validaciones ligeras de UI (ej. estados de error).
- Siguen sin conocer casos de uso de negocio.

### 3.3. Organisms (`components/organisms`)

Unen moléculas para estructuras funcionales.

Ejemplos ligados a autenticación:

- `LoginForm`
- `RegisterForm`
- `MfaForm`
- `ProfileForm`

Responsabilidades:

- Manejar estado local de formulario.
- Invocar **hooks** de dominio (por ejemplo, `useLogin`, `useRegister`) expuestos desde `lib/auth`.
- Gestionar errores y loading states.

### 3.4. Templates (`components/templates`)

Definen layout de páginas.

Ejemplos:

- `AuthPageTemplate`:
  - Layout centrado con card para `LoginForm`, `RegisterForm`, `MfaForm`.
- `DashboardTemplate`:
  - App bar + sidebar + área de contenido (pensando en panel administrativo futuro).

Reglas:

- Reciben organisms como children.
- No contienen lógica de negocio; solo layout y composición.

### 3.5. Pages (`src/app/...`)

Rutas de Next.js.

Ejemplos:

- `/auth/login/page.tsx`
- `/auth/register/page.tsx`
- `/auth/mfa/page.tsx`
- `/profile/page.tsx`

Responsabilidades:

- Seleccionar template apropiado.
- Conectar con router / metadata.
- No repetir lógica de formularios; utilizar organisms.

---

## 4. Capa de acceso a APIs y auth

### 4.1. Cliente HTTP (`lib/api`)

```text
src/lib/api/
  client.ts         # axios/fetch wrapper
  auth_api.ts       # funciones login, register, mfa, me
```

Reglas:

- `client.ts` configura:
  - `baseURL` del backend.
  - Interceptores para:
    - Adjuntar `Authorization: Bearer <access_token>`.
    - Manejar 401/403 (refresco de token, redirección a login).
- `auth_api.ts` exporta funciones:
  - `login(payload)`, `register(payload)`, `verifyMfa(payload)`, `getProfile()`.

### 4.2. Capa de dominio de UI (`lib/auth`)

```text
src/lib/auth/
  useLogin.ts
  useRegister.ts
  useMfa.ts
  useProfile.ts
  auth_context.tsx
```

Patrones:

- Cada hook implementa un caso de uso específico desde el punto de vista de UI.
- Internamente llaman a `auth_api.ts`.
- Manejan:
  - `isLoading`, `error`, `onSuccess`.
- `auth_context.tsx`:
  - Almacena estado de sesión (usuario actual, access token en memoria).
  - Opcionalmente integra refresh token vía cookie httpOnly (manejado por el backend).

---

## 5. Patrones específicos para la evolución

### 5.1. Pattern: “UI Use Case Hook”

Para cada “capacidad” de la interfaz, crear un hook dedicado en `lib/`:

- `useLogin`, `useRegister`, `useChangePassword`, etc.

Beneficios:

- Los organisms solo conocen hooks, no detalles de API.
- Permite a un agente de IA o dev localizar rápidamente dónde modificar un flujo.

### 5.2. Pattern: “Thin Page, Rich Template/Organism”

Regla general:

- Las páginas (Next) solo ensamblan:
  - Template adecuado.
  - Organisms.
- La lógica de negocio de UI debe vivir en:
  - Hooks (`lib`) y organisms.

Ejemplo:

- Agregar nueva pantalla de “Gestión de dispositivos confiables”:
  - Crear `DeviceListOrganism`.
  - Crear `useTrustedDevices` en `lib/auth`.
  - Página solo importa y coloca el organism en `DashboardTemplate`.

### 5.3. Pattern: “Design Tokens & Theming”

En `styles/` o `config/theme.ts`:

- Definir tokens:
  - Colores, tipografía, espaciados, radius.
- Todos los átomos deben usar estos tokens.
- Facilita mantener la consistencia UX web/móvil requerida en el documento.

---

## 6. Reglas de evolución funcional

### 6.1. Añadir nuevo flujo de autenticación

Ejemplo: recuperación de PIN/contraseña.

Checklist:

1. **Backend**:
   - Nuevo caso de uso: `RequestPasswordResetUseCase`, `ResetPasswordUseCase`.
   - Endpoints: `/auth/password/reset/request`, `/auth/password/reset/confirm`.
2. **Frontend**:
   - Hook: `useRequestPasswordReset`, `useResetPassword`.
   - Organisms: `PasswordResetRequestForm`, `PasswordResetForm`.
   - Pages:
     - `/auth/password/reset/request`
     - `/auth/password/reset/confirm`
   - Template: reutilizar `AuthPageTemplate`.

### 6.2. Añadir MFA más avanzado

- Backend:
  - Extender `MfaConfig` y `MfaService`.
- Frontend:
  - Nuevos átomos (ej. QRCodeDisplay).
  - Nuevos organisms (setup MFA, confirm codes).
  - Nuevos hooks (`useSetupMfa`).

---

## 7. Calidad, rendimiento y UX

### 7.1. Usabilidad

- Formularios de registro y KYC deben permitir que 90–95 % de usuarios completen proceso en pocos minutos, en línea con objetivos de onboarding del documento.
- Validaciones claras, mensajes de error en `FormField` (moléculas), feedback inmediato.

### 7.2. Rendimiento

- Utilizar **carga diferida** de componentes pesados donde tenga sentido.
- Cachear datos de perfil y usuario en context/hook para reducir llamadas repetidas (también alineado con las ideas de caching del backend).

### 7.3. Testing de UI

  - Átomos y moléculas (render, props).
  - Organisms (simular inputs, verificar llamadas a hooks).
  - Flujos críticos: registro + KYC simulado + login + MFA.

#### 7.3.1. Requisitos de cobertura y calidad

- **Cobertura mínima:** >= 85% en líneas, statements, funciones y branches para el scope del cambio (módulo/componente afectado).
- **Herramienta de coverage:** Se usa **c8** (V8-nativo) con loader **tsx** para Mocha. Ejecutar con `npm run test:coverage`. Umbrales configurados en `package.json`. _Migrado desde nyc/ts-node en HU-FE-00 por compatibilidad con ESM y Node >=20._
- **Complejidad ciclomática:** < 10 por función/método (verificar con SonarJS ESLint plugin).
- **Tamaño de archivo:** Máximo 500 líneas por archivo (dividir/refactor si se excede).

#### 7.3.2. Tipos de tests obligatorios

Para cada componente/hook nuevo o modificado, incluir tests para:

1. **Casos positivos (happy path):**
   - Render con props válidas produce output esperado
   - Ejemplo: `<Button onClick={handler}>Click</Button>` → botón renderiza texto "Click"
   - Ejemplo: `useLogin` con credenciales válidas → token JWT retornado

2. **Casos negativos (error handling):**
   - Props inválidas o errores de API
   - Ejemplo: `<TextField value={null}>` → no crash, muestra string vacío
   - Ejemplo: `useLogin` con 401 → muestra mensaje "Credenciales incorrectas"
   - Ejemplo: Network error → muestra mensaje de conexión fallida

3. **Edge cases (valores límite):**
   - Props en los límites de validación
   - Ejemplo: `<TextField maxLength={50}>` → trunca en 50 caracteres
   - Ejemplo: Componente sin children → no crash, render vacío o placeholder
   - Ejemplo: Lista con 0 items → muestra estado vacío

4. **Casos de interacción (user interactions):**
   - Eventos de usuario
   - Ejemplo: Click en botón → callback invocado con argumentos correctos
   - Ejemplo: Cambio en input → estado actualizado y validación ejecutada
   - Ejemplo: Submit de formulario → loading state activado, luego éxito/error

5. **Casos de estado (state transitions):**
   - Transiciones entre estados del componente
   - Ejemplo: Form idle → loading → success
   - Ejemplo: Form idle → loading → error → retry → success

6. **Casos de accesibilidad:**
   - ARIA labels, roles, keyboard navigation
   - Ejemplo: Button tiene role="button" y responde a Enter/Space
   - Ejemplo: Form inputs tienen labels asociados
   - Ejemplo: Error messages tienen aria-live="polite"

7. **Casos de responsive/theming:**
   - Diferentes breakpoints o temas
   - Ejemplo: Component adapta layout en mobile vs desktop
   - Ejemplo: Dark mode aplica colores correctos

#### 7.3.3. Estructura de tests (ejemplos)

**Unit test - Atom (Button):**
```tsx
describe('Button', () => {
  it('should render with default props', () => {
    const element = React.createElement(Button, { children: 'Click' });
    const html = ReactDOMServer.renderToStaticMarkup(element);
    expect(html).to.contain('Click');
  });

  it('should render as disabled when disabled prop is true', () => {
    const element = React.createElement(Button, { children: 'Click', disabled: true });
    const html = ReactDOMServer.renderToStaticMarkup(element);
    expect(html).to.contain('disabled');
  });

  it('should apply custom className', () => {
    const element = React.createElement(Button, { children: 'Click', className: 'custom' });
    const html = ReactDOMServer.renderToStaticMarkup(element);
    expect(html).to.contain('custom');
  });

  it('should handle empty children gracefully', () => {
    const element = React.createElement(Button, {});
    const html = ReactDOMServer.renderToStaticMarkup(element);
    expect(html).to.contain('<button');
  });
});
```

**Unit test - Organism (LoginForm):**
```tsx
describe('LoginForm', () => {
  it('should render email and password fields', () => {
    const mockLogin = sinon.stub();
    const element = React.createElement(LoginForm, { onLogin: mockLogin });
    const html = ReactDOMServer.renderToStaticMarkup(element);
    
    expect(html).to.contain('email');
    expect(html).to.contain('password');
  });

  it('should show error when login fails', () => {
    const mockLogin = sinon.stub().rejects(new Error('Invalid credentials'));
    const element = React.createElement(LoginForm, { 
      onLogin: mockLogin,
      error: 'Invalid credentials'
    });
    const html = ReactDOMServer.renderToStaticMarkup(element);
    
    expect(html).to.contain('Invalid credentials');
  });

  it('should disable submit button when loading', () => {
    const mockLogin = sinon.stub();
    const element = React.createElement(LoginForm, { 
      onLogin: mockLogin,
      isLoading: true
    });
    const html = ReactDOMServer.renderToStaticMarkup(element);
    
    expect(html).to.contain('disabled');
  });
});
```

**Integration test - Hook (useLogin):**
```tsx
describe('useLogin', () => {
  let apiStub: sinon.SinonStub;

  beforeEach(() => {
    apiStub = sinon.stub(api, 'login');
  });

  afterEach(() => {
    apiStub.restore();
  });

  it('should return token when login succeeds', async () => {
    // Arrange
    apiStub.resolves({ token: 'jwt-token', user: { id: '1', email: 'test@example.com' } });
    
    // Act
    const result = await useLogin.execute('test@example.com', 'password123');
    
    // Assert
    expect(result.token).to.equal('jwt-token');
    expect(apiStub).to.have.been.calledOnce;
  });

  it('should throw error when credentials are invalid', async () => {
    // Arrange
    apiStub.rejects({ status: 401, message: 'Invalid credentials' });
    
    // Act & Assert
    await expect(useLogin.execute('test@example.com', 'wrong')).to.be.rejectedWith('Invalid credentials');
  });

  it('should handle network errors gracefully', async () => {
    // Arrange
    apiStub.rejects(new Error('Network error'));
    
    // Act & Assert
    await expect(useLogin.execute('test@example.com', 'password123')).to.be.rejectedWith('Network error');
  });
});
```

#### 7.3.4. Validación antes de commit

Ejecutar **siempre** antes de crear PR:
```bash
# Formato
npm run format

# Linting
npm run lint

# Type checking
npm run type-check

# Tests con cobertura
npm run test:coverage

# Verificar que todos pasen sin errores
npm run quality:check
```

#### 7.3.5. Patrón de pruebas AAA

- **Regla:** Todos los tests unitarios y de integración deben seguir el patrón **AAA**: _Arrange_ (preparar fixtures, mocks y entradas), _Act_ (ejecutar el componente/hook/caso de uso) y _Assert_ (verificar la salida/estado esperado).
- **Tests unitarios:** Mantenerlos enfocados y deterministas; en `Arrange` usar helpers/mocks ligeros, en `Act` renderizar o invocar el hook/caso de uso, y en `Assert` comprobar la salida renderizada, el estado o los valores devueltos.
- **Tests de integración:** Separar claramente la preparación del entorno (mock de API, estado de auth, router), ejecutar el flujo completo y limpiar recursos en el `teardown`. Usar fixtures para centralizar la lógica de `Arrange`.
- **Convenciones:** Usar nombres descriptivos para los tests (p. ej. `should_render_with_default_props_when_disabled`) y comentarios opcionales `// Arrange // Act // Assert` para mejorar la legibilidad.

---

## 8. Convenciones para agentes de IA

- Siempre que se pida “crear una nueva pantalla”, seguir esta secuencia:
  1. Definir hook de dominio en `src/lib/...`.
  2. Crear organism que use ese hook.
  3. Insertar organism en un template existente o uno nuevo.
  4. Crear página que use el template y el organism.
- Mantener nombres de ruta coherentes con los flujos de backend:
  - `/auth/login` → `POST /auth/login`
  - `/auth/register` → `POST /auth/register`
  - `/auth/mfa` → `POST /auth/mfa/verify`

---

## 9. Sincronización con arquitectura TO‑BE

- Mantener paridad funcional entre web y apps móviles para los flujos principales de autenticación y perfil, tal como se exige en las capacidades de interfaz web del TO‑BE.
- Al agregar nuevas capacidades de seguridad (ej. gestión de dispositivos, alertas), hacerlo siempre:
  - Con nuevos hooks + organisms.
  - Respetando Atomic Design y evitando lógica ad‑hoc en páginas.
```