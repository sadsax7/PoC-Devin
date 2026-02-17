SYSTEM INSTRUCTION:
Actúa como un Desarrollador Frontend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-FE-04
Work Item Type: User Story
Title: Implementar pantalla principal privada con perfil y cierre de sesión  
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\FrontEnd
Iteration: PoC\Sprint 1
Tags: [NextJS, AtomicDesign, Tailwind]

DESCRIPTION:
Como **Usuario Autenticado**,
Quiero **ver mi información de perfil y tener la opción de cerrar sesión**,
Para **confirmar que he ingresado correctamente y gestionar mi sesión de forma segura.**

ACCEPTANCE CRITERIA:
1. **Protección de Ruta:**
   - La página `/dashboard` debe ser accesible SOLO si hay `access_token` válido en el Context de autenticación.
   - Si no hay token → Redirigir a `/auth/login` automáticamente (middleware o useEffect).
   - Si token existe pero está expirado → Intentar renovar con `refresh_token`. Si falla → Logout automático y redirigir a login.

2. **Consumo de Endpoint `/users/me`:**
   - **Request:** `GET /users/me` con header `Authorization: Bearer <access_token>`.
   - **Respuesta Exitosa (`200 OK`):** Mostrar datos del usuario.
   - **Errores:**
     - `401 Unauthorized` (token expirado): Intentar renovar token. Si falla → Logout.
     - `404 Not Found`: Mostrar "Usuario no encontrado. Tu cuenta puede haber sido eliminada." y botón "Volver a login".
     - `500 Internal Server Error`: Mostrar "Error del servidor. Intenta recargar la página.".

3. **UI del Dashboard:**
   - **Layout:** Usar `<main>` como contenedor (consistente con `src/app/page.tsx`). Contenido en `<section>` con clases `flex min-h-screen flex-col items-center justify-center p-6 bg-background text-foreground`.
   - **Header/Logo:** Logo Next.js en la parte superior (Image component, src="/next.svg", className="dark:invert mb-8").
   - **Sección de Perfil:**
     - **Nombre:** Título grande con clases `text-4xl font-bold tracking-tight` (consistente con título de HeroSection).
     - **Teléfono:** Texto secundario con clases `text-lg text-zinc-600 dark:text-zinc-400`.
     - **Email:** Texto secundario (si existe), mismo estilo que teléfono. Si null → "Email no proporcionado" en texto más tenue.
     - **Estado KYC:** Badge con colores:
       - "pending" → Amarillo (bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200), "Verificación Pendiente".
       - "approved" → Verde (bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200), "Verificado".
       - "rejected" → Rojo (bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200), "Verificación Rechazada".
     - **MFA:** Badge con colores:
       - `true` → Verde, "MFA Habilitado".
       - `false` → Gris (bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200), "MFA Deshabilitado".
   - **Fecha de Creación:** Texto pequeño con clases `text-sm text-zinc-600 dark:text-zinc-400`, formato "Miembro desde [fecha]".
   - **Botón Logout:** Usar `Button` variant="outline" con texto "Cerrar Sesión", posicionado al final del contenido (mt-8).

4. **Lógica de Logout:**
   - **Al hacer clic en "Cerrar Sesión":**
     1. Limpiar `access_token` y `refresh_token` del Context.
     2. Limpiar cookies (si `refresh_token` está en cookie httpOnly).
     3. Opcional: Llamar endpoint `POST /auth/logout` (si se implementa en backend para invalidar tokens).
     4. Redirigir a `/auth/login`.
   - **Logout Automático (Token Expirado):**
     - Si `GET /users/me` retorna `401 Unauthorized` y el intento de renovar falla → Ejecutar logout automático.
     - Mostrar toast/notificación: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.".

5. **Estados Visuales:**
   - **Loading:** Skeleton loaders para nombre, teléfono, badges mientras carga `/users/me`.
   - **Success:** Datos mostrados, botones interactivos.
   - **Error:** Mensaje de error con botón "Reintentar" o "Volver a login".

6. **Estructura Atomic Design:**
   - **Átomos:**
     - `Badge`: Componente para badges de KYC y MFA con variants (colors). Props: `variant`, `children`.
     - `Skeleton`: Loader placeholder para textos y badges (opcional, puede usar simple CSS animation).
     - `Button`: Usar componente existente de HU-FE-01.
   - **Moléculas:**
     - `ProfileInfo`: Agrupa nombre, teléfono, email con estilos consistentes.
     - `StatusBadges`: Agrupa badges de KYC y MFA en un contenedor flex.
   - **Organismos:**
     - `DashboardContent`: Contenido completo del dashboard (logo + ProfileInfo + StatusBadges + fecha + botón logout).
   - **Páginas:**
     - `src/app/dashboard/page.tsx`: Renderiza directamente `<main><DashboardContent /></main>` (consistente con patrón de HU-FE-01).

7. **Navegación:**
   - Botón "Cerrar Sesión" con `onClick` que ejecuta logout (no href).
   - Futuro: Links a secciones de transacciones, configuración, etc.

8. **Accesibilidad:**
   - Botón "Cerrar Sesión" con `aria-label="Cerrar sesión"`.
   - Badges con `aria-label` descriptivos (ej: "Estado de verificación KYC: Verificado").
   - Mensajes de error con `role="alert"`.
   - Estados de foco visibles en todos los elementos interactivos.

9. **UI Use Case Hook:**
   - Crear `src/lib/auth/useProfile.ts`:
     - Estado: `isLoading`, `error`, `user`.
     - Función: `fetchProfile() -> Promise<void>`.
     - Llama a `fetch('/api-base-url/users/me', { headers: { 'Authorization': 'Bearer ' + token } })`.
   - Actualizar o usar `src/lib/auth/useAuth.ts`:
     - Estado: `isAuthenticated`, `accessToken`, `user`.
     - Función: `logout() -> void` (limpia tokens, Context, cookies si aplica).
     - Función: `refreshToken() -> Promise<void>` (llamar cuando 401 con access_token expirado).
   - Usar `useRouter` de `next/navigation` para redirecciones post-logout.

DEINITION OF READY
1. ✅ Mecanismo de almacenamiento de Token implementado en HU-FE-03 (Context API con `access_token` y `refresh_token`).
2. ✅ Endpoint `/users/me` disponible (ver HU-BE-03).
3. ✅ Diseño de badges de KYC y MFA aprobado (colores, íconos).

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
11. **Accesibilidad:** Dashboard navegable con teclado, badges con aria-labels, contraste WCAG AA.
12. **Ciclo de sesión completo:** Probado flujo Login → Dashboard → Logout → Login.
13. **Token Refresh:** Probado renovación automática cuando `access_token` expira.

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