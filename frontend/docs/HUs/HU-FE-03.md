SYSTEM INSTRUCTION:
Actúa como un Desarrollador Frontend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-FE-03
Work Item Type: User Story
Title: Implementar flujo de Login con ruta condicional a pantalla MFA 
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\FrontEnd
Iteration: PoC\Sprint 1
Tags: [NextJS, AtomicDesign, Tailwind]

DESCRIPTION:
Como **Usuario Registrado**,
Quiero **ingresar mis credenciales y completar MFA si está habilitado**,
Para **acceder a mi cuenta de forma segura.**

ACCEPTANCE CRITERIA:
1. **Paso 1: Formulario de Login (`/auth/login`):**
   - **Layout:** Usar `<section>` con clases `flex min-h-screen flex-col items-center justify-center p-6 bg-background text-foreground` (consistente con HeroSection y RegisterForm).
   - **Logo:** Incluir logo Next.js placeholder en la parte superior (Image component, `src="/next.svg"`, className="dark:invert mb-8").
   - **Campos:**
     - `phone`: Input de texto con placeholder "ej: +573001234567" (sin máscara, validación E.164 en tiempo real).
     - `password`: Input de tipo password con toggle de visibilidad.
   - **Validaciones:**
     - Teléfono: formato E.164 requerido.
     - Contraseña: no vacío (validación backend es más estricta).
   - **Botón Principal:** "Ingresar" (sólido naranja, `Button` variant="solid", fullWidth en mobile).
   - **Botón Secundario:** "¿No tienes cuenta? Regístrate" (outline naranja, `Button` variant="outline", href="/auth/register", posicionado DEBAJO del botón principal).

2. **Lógica de Respuesta del Endpoint `POST /auth/login`:**
   - **Caso A: MFA Deshabilitado (`200 OK` con `access_token`):**
     - Almacenar `access_token` y `refresh_token` en memoria (Context API).
     - Almacenar `refresh_token` en cookie httpOnly (si el backend lo configura).
     - Redirigir a `/dashboard`.
   - **Caso B: MFA Habilitado (`200 OK` con `temp_token` y `mfa_required: true`):**
     - Almacenar `temp_token` en estado temporal (no en Context, solo en componente).
     - Transicionar a Paso 2 (pantalla MFA) SIN cambiar de ruta (misma página, cambio de vista).
   - **Caso C: Errores:**
     - `401 Unauthorized`: Mostrar "Credenciales inválidas. Verifica tu teléfono y contraseña.".
     - `404 Not Found`: Mostrar "Teléfono no registrado. ¿Quieres [registrarte](/auth/register)?".
     - `423 Locked`: Mostrar "Tu cuenta está bloqueada. Contacta soporte.".
     - `500 Internal Server Error`: Mostrar "Error del servidor. Intenta nuevamente más tarde.".

3. **Paso 2: Verificación MFA (misma ruta `/auth/login`):**
   - **UI:**
     - Título: "Verificación de Seguridad".
     - Subtítulo: "Ingresa el código de 6 dígitos generado por tu aplicación de autenticación".
     - Input de OTP: 6 campos individuales (1 dígito por campo), auto-focus en el primero, auto-advance al siguiente.
   - **Comportamiento del Input OTP:**
     - Solo acepta números (0-9).
     - Al llenar el sexto campo, auto-submit (llamar endpoint MFA).
     - Permitir pegar código completo (ej: "123456") que distribuye dígitos automáticamente.
     - Botón "Verificar" (sólido naranja) como alternativa al auto-submit.
   - **Endpoint:** `POST /auth/mfa/verify` con `temp_token` y `code`.
   - **Manejo de Respuestas:**
     - `200 OK`: Almacenar `access_token` y `refresh_token`, redirigir a `/dashboard`.
     - `401 Unauthorized` (código inválido): Mostrar "Código incorrecto. Intentos restantes: X". Limpiar inputs.
     - `429 Too Many Requests`: Mostrar "Demasiados intentos fallidos. Redirigiendo a login...". Redirigir a Paso 1 después de 3 segundos.
     - `401 Unauthorized` (temp_token expirado): Mostrar "Sesión expirada. Vuelve a iniciar sesión.". Redirigir a Paso 1.

4. **Estados Visuales:**
   - **Login Form:**
     - Idle: Campos vacíos, botón "Ingresar" deshabilitado.
     - Typing: Botón habilitado si ambos campos válidos.
     - Submitting: Spinner en botón, "Iniciando sesión...", campos deshabilitados.
     - Error: Mensaje de error con ícono X rojo.
   - **MFA Form:**
     - Idle: Inputs vacíos, focus en primer campo.
     - Typing: Auto-advance entre campos.
     - Submitting: Spinner sobre inputs, "Verificando...", campos deshabilitados.
     - Error: Mensaje de error con ícono X rojo, contador de intentos visible.
     - Success: Mensaje "Verificación exitosa, redirigiendo...", checkmark verde.

5. **Estructura Atomic Design:**
   - **Átomos:**
     - `OtpDigitInput`: Input de 1 dígito con estilos de foco y error (usar TextField base con max-length=1).
     - `Button`: Usar componente existente de HU-FE-01.
     - `TextField`: Usar componente creado en HU-FE-02.
   - **Moléculas:**
     - `OtpCodeInput`: Grupo de 6 `OtpDigitInput` con lógica de auto-advance y paste.
   - **Organismos:**
     - `LoginForm`: Formulario de login (Paso 1) con logo, campos y botones.
     - `MfaForm`: Formulario de MFA con `OtpCodeInput` y logo (Paso 2).
     - `LoginFlowManager`: Componente que maneja transición entre `LoginForm` y `MfaForm` basado en estado (sin cambio de ruta).
   - **Páginas:**
     - `src/app/auth/login/page.tsx`: Renderiza directamente `LoginFlowManager` (consistente con patrón de HU-FE-01 y HU-FE-02).

6. **Navegación:**
   - Botón "¿No tienes cuenta? Regístrate" en LoginForm (variant="outline", href="/auth/register").
   - Botón "Volver a login" en MfaForm (variant="outline", onClick que resetea estado a Paso 1).
   - Redirección automática a `/dashboard` después de login/MFA exitoso (usar `useRouter` de `next/navigation`).

7. **Accesibilidad:**
   - Labels asociados a inputs con `htmlFor`.
   - Inputs OTP con `aria-label="Dígito X de 6"`.
   - Mensajes de error con `role="alert"` y `aria-live="assertive"`.
   - Estados de foco visibles en todos los inputs.
   - Contador de intentos con `aria-live="polite"`.

8. **UI Use Case Hooks:**
   - Crear `src/lib/auth/useLogin.ts`:
     - Estado: `isLoading`, `error`, `needsMfa`, `tempToken`.
     - Función: `login(phone, password) -> Promise<void>`.
     - Llama a `fetch('/api-base-url/auth/login', { method: 'POST', ... })`.
   - Crear `src/lib/auth/useMfa.ts`:
     - Estado: `isLoading`, `error`, `attemptsRemaining`.
     - Función: `verifyMfa(tempToken, code) -> Promise<void>`.
     - Llama a `fetch('/api-base-url/auth/mfa/verify', { method: 'POST', ... })`.
   - Usar `useRouter` de `next/navigation` para redirecciones.

DEINITION OF READY
1. ✅ Contrato de respuesta de `POST /auth/login` definido (ver HU-BE-02 Acceptance Criteria #6).
2. ✅ Contrato de respuesta de `POST /auth/mfa/verify` definido (ver HU-BE-02 Acceptance Criteria #6).
3. ✅ Diseño del componente de input de OTP (6 dígitos) definido en wireframes.

DEFINITION OF DONE (Global Policy):
1. **Formato:** **Prettier** ejecutado en todo el código (`npm run format`).
2. **Linting:** **ESLint** pasando sin errores ni warnings (`npm run lint`).
3. **Typing:** **TypeScript Strict Mode** sin errores (`npm run type-check`).
4. **Cobertura de Pruebas:** >= 85% en líneas, statements, funciones y branches (medido con `nyc`).
5. **Framework de Testing:** Usar **Mocha + Chai + Sinon** (NO Jest).
6. **Tipos de Tests:** Incluir casos positivos, negativos, edge cases, interacciones, estados, accesibilidad y variaciones de props (ver FRONTEND-GUIDELINES.md sección 7.3.2).
7. **Docs:** Componentes documentados con **TSDoc** (props, comportamiento, ejemplos).
8. **Límites:** Ningún archivo excede las 500 líneas.
9. **Validación Local:** Ejecutar `npm run quality:check` antes de commit.
10. **Responsive verificado:** Probar en viewports móvil (375px) y desktop (1024px).
11. **Accesibilidad:** Formularios navegables con teclado, OTP con auto-focus y auto-advance, errores anunciados.
12. **Integración con Backend:** Flujo completo probado con servidor local (HU-BE-02).

-----------------------------------------------------------------------
⚠️ CRITICAL INSTRUCTIONS - READ BEFORE STARTING:

1. **DO NOT DELETE CONFIGURATION FILES:**
   - `Frontend/web/.mocharc.json` (Mocha test configuration)
   - `Frontend/web/.nycrc.json` (Coverage thresholds)
   - `PoC/.gitignore` (project-wide ignore rules)
   - ANY file in `Frontend/web/` root that ends in `.json`, `.mjs`, `.ts`, `.config.*`
   - If you think a config file should be removed, STOP and ask first.

2. **MANDATORY REFERENCES:**
   - Read `Frontend/docs/FRONTEND-GUIDELINES.md` sections 7.1 (Atomic Design) and 7.3 (Testing) BEFORE coding.
   - Read `agents.md` section 5.2.7.1 for test type requirements and examples.
   - Follow Atomic Design hierarchy: atoms → molecules → organisms → templates → pages.

3. **QUALITY GATES (BLOCKERS):**
   - Coverage >= 85% (nyc npm test)
   - All 7 test types implemented: positive, negative, edge cases, interactions, state, accessibility, props variations.
   - TypeScript strict mode (tsc --noEmit must pass).
   - All DoD checks passing before committing.

4. **TESTING FRAMEWORK:**
   - Use Mocha + Chai + Sinon (NOT Jest).
   - Pattern: AAA (Arrange-Act-Assert).
   - Name tests: `should_<expected>_when_<condition>`.
   - Use proxyquire for Next.js mocks.

-----------------------------------------------------------------------

YOUR TASK:
1. Analiza los archivos actuales del repositorio.
2. Genera el código necesario para completar este Work Item.
3. Genera los tests correspondientes (7 tipos obligatorios).
4. Asegúrate que el código entregado cumple con los Definition of Done detallados en el Work Item.
5. Ejecuta validación local: `npm run quality:check`.
6. Confirma qué archivos has creado o modificado.