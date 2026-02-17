SYSTEM INSTRUCTION:
Actúa como un Desarrollador Frontend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-FE-02
Work Item Type: User Story
Title: Desarrollar Organismo de Registro con Validación y Feedback 
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\FrontEnd
Iteration: PoC\Sprint 1
Tags: [NextJS, AtomicDesign, Tailwind]

DESCRIPTION:
Como **Usuario Nuevo**,
Quiero **completar mi registro en una interfaz guiada con validaciones en tiempo real**,
Para **crear mi cuenta exitosamente y recibir confirmación inmediata.**

ACCEPTANCE CRITERIA:
1. **Estructura del Formulario:**
   - **Campos:**
     - `phone`: Input de texto con placeholder "ej: +573001234567" (sin máscara automática, validación E.164 en tiempo real).
     - `password`: Input de tipo password con toggle de visibilidad (ícono ojo).
     - `confirm_password`: Input de tipo password para confirmar coincidencia.
     - `email` (opcional): Input de email con validación de formato.
     - `name` (opcional): Input de texto (máximo 100 caracteres).
   - **Layout:** Usar `<section>` como contenedor principal con clases `flex min-h-screen flex-col items-center justify-center p-6 bg-background text-foreground` (consistente con HeroSection). Formulario en columna (flex-col), campos apilados verticalmente, espaciado consistente (gap-4).

2. **Validaciones en Tiempo Real:**
   - **Teléfono:**
     - Formato E.164: debe empezar con `+` y contener código de país + número (ej: +573001234567).
     - Mostrar error si formato inválido: "Formato de teléfono inválido. Usa +[código país][número]".
   - **Contraseña:**
     - Mínimo 8 caracteres, máximo 128.
     - Al menos 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial.
     - Mostrar indicador visual de fortaleza: débil (rojo), media (amarillo), fuerte (verde).
     - Mensajes específicos por regla incumplida.
   - **Confirmar Contraseña:**
     - Debe coincidir con `password`.
     - Mostrar error si no coincide: "Las contraseñas no coinciden".
   - **Email (opcional):**
     - Si se proporciona, validar formato: regex `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`.
     - Máximo 255 caracteres.

3. **Estados del Formulario:**
   - **Idle:** Formulario vacío, botón "Registrarse" deshabilitado (`disabled` prop del Button).
   - **Typing:** Usuario escribiendo, validaciones en tiempo real, botón habilitado si todos los campos válidos.
   - **Submitting:** Botón deshabilitado, mostrar spinner naranja (`var(--primary)`) inline o sobre el texto "Registrarse", campos deshabilitados.
   - **Success:** Mensaje de éxito con ícono checkmark verde, "¡Cuenta creada exitosamente! Redirigiendo...", formulario oculto o con overlay.
   - **Error:** Mensaje de error con ícono X rojo debajo del botón submit, texto específico según error del backend, formulario sigue visible para corrección.

4. **Integración con Backend:**
   - **Endpoint:** `POST /auth/register` (HU-BE-01).
   - **Request Body:**
     ```json
     {
       "phone": "+573001234567",
       "password": "SecureP@ss123",
       "email": "user@example.com",
       "name": "Juan Pérez"
     }
     ```
   - **Manejo de Respuestas:**
     - `201 Created`: Mostrar mensaje de éxito por 2 segundos, luego redirigir a `/auth/login`.
     - `400 Bad Request` (KYC rejected): Mostrar "Tu número de teléfono no pasó la verificación KYC. Contacta soporte.".
     - `409 Conflict` (phone exists): Mostrar "Este teléfono ya está registrado. ¿Quieres [iniciar sesión](/auth/login)?".
     - `422 Unprocessable Entity`: Mostrar errores de validación campo por campo (mapear `detail` array de Pydantic).
     - `500 Internal Server Error`: Mostrar "Error del servidor. Intenta nuevamente más tarde.".

5. **Estructura Atomic Design:**
   - **Átomos:**
     - `TextField`: Input con label, error message, opcional suffix (ej: ícono ojo).
     - `Button`: Usar componente existente de HU-FE-01 (variants: "solid" | "outline", fullWidth prop).
     - `ErrorMessage`: Componente para mensajes de error (texto rojo, ícono X opcional).
     - `SuccessMessage`: Componente para mensajes de éxito (texto verde, ícono checkmark opcional).
   - **Moléculas:**
     - `FormField`: Agrupa TextField + Label + ErrorMessage + HelperText.
     - `PasswordStrengthIndicator`: Barra de progreso con colores débil (red)/media (yellow)/fuerte (green).
   - **Organismos:**
     - `RegisterForm`: Formulario completo con validaciones, estados y submit. Incluye logo Next.js como en HeroSection.
   - **Páginas:**
     - `src/app/auth/register/page.tsx`: Renderiza directamente `RegisterForm` (sin template adicional, consistente con `src/app/page.tsx` de HU-FE-01).

6. **Navegación:**
   - Botón secundario "¿Ya tienes cuenta? Ingresar" que usa componente `Button` con `variant="outline"` y `href="/auth/login"` (consistente con botón "Ingresar" de HeroSection).
   - Posicionar botón secundario DEBAJO del botón "Registrarse" principal, con texto más pequeño y centrado.
   - Redirección automática a `/auth/login` después de registro exitoso (2 segundos con `setTimeout` y `router.push()`).

7. **Accesibilidad:**
   - Todos los inputs con `<label>` asociado vía `htmlFor`.
   - Mensajes de error con `role="alert"` y `aria-live="polite"`.
   - Botón submit con `aria-busy="true"` durante submitting.
   - Indicador de fortaleza de contraseña con `aria-label` descriptivo.
   - Contraste WCAG AA en todos los textos y estados de foco visibles.

8. **UI Use Case Hook:**
   - Crear `src/lib/auth/useRegister.ts`:
     - Estado: `isLoading`, `error`, `success`.
     - Función: `register(data: RegisterFormData) -> Promise<void>`.
     - Llama a `fetch('/api-base-url/auth/register', { method: 'POST', body: JSON.stringify(data) })`.
     - Maneja errores (mapeo de status codes a mensajes) y transiciones de estado.
   - Usar `useRouter` de `next/navigation` para redirección post-registro.

DEINITION OF READY
1. ✅ Contrato JSON de entrada del endpoint `POST /auth/register` conocido (ver HU-BE-01 Acceptance Criteria #7).
2. ✅ Button atom implementado en HU-FE-01 con variants `solid` y `outline`.
3. ✅ Componentes Átomos (TextField, ErrorMessage, SuccessMessage) diseñados siguiendo patrones de Button.

DEFINITION OF DONE (Global Policy):
1. **Formato:** **Prettier** ejecutado en todo el código (`npm run format`).
2. **Linting:** **ESLint** pasando sin errores ni warnings (`npm run lint`).
3. **Typing:** **TypeScript Strict Mode** sin errores (`npm run type-check`).
4. **Cobertura de Pruebas:** >= 85% en líneas, statements, funciones y branches (medido con `nyc`).
5. **Framework de Testing:** Usar **Mocha + Chai + Sinon** (NO Jest).
6. **Tipos de Tests:** Incluir casos positivos, negativos, edge cases, interacciones, estados, accesibilidad y variaciones de props (ver FRONTEND-GUIDELINES.md sección 7.3.2).
7. **Docs:** Componentes documentados con **TSDoc** (props, comportamiento, ejemplos).
8. **Límites:** Ningún archivo excede las 500 líneas.
9. **Validación Local:** Ejecutar `npm run quality:check` antes de commit (format, lint, type-check, test:coverage).
10. **Responsive verificado:** Probar en viewports móvil (375px) y desktop (1024px) mínimo.
11. **Accesibilidad:** Formulario navegable con teclado, errores anunciados, contraste WCAG AA.
12. **Integración con Backend:** Probado con servidor local (HU-BE-01) para flujo completo.

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