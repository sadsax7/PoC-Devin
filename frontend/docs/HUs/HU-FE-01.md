SYSTEM INSTRUCTION:
Actúa como un Desarrollador Frontend Senior parte de un equipo híbrido.
Acabas de recibir la asignación de un nuevo Work Item desde Azure DevOps Board.
Tu objetivo es analizar los requisitos, identificar el contexto arquitectónico basado en el 'Area Path', los 'Tags' y las guidelines del proyecto, y entregar el código que satisfaga los 'Acceptance Criteria' y los 'Definition of Done'.

-----------------------------------------------------------------------
Azure DevOps Work Item Details
-----------------------------------------------------------------------
ID: HU-FE-01
Work Item Type: User Story
Title: Implementar página de inicio (Landing) con opciones de acceso
State: Active
Assigned To: Devin (AI Agent)
Area Path: BilleteraVirtual\FrontEnd
Iteration: PoC\Sprint 1
Tags: [NextJS, AtomicDesign, Tailwind]

DESCRIPTION:
Como **Usuario Visitante**,
Quiero **ver una pantalla de bienvenida donde pueda elegir entre registrarme o iniciar sesión**,
Para **comenzar mi interacción con la billetera.**

ACCEPTANCE CRITERIA:
1.  **Diseño:** Hero section simple con:
    - **Título:** "Bienvenido a Billetera Virtual"
    - **Subtítulo:** "Tu dinero seguro, rápido y fácil de usar"
    - **Logo:** Usar el logo de Next.js (`/next.svg`) como placeholder hasta que esté disponible el logo de la billetera.

2.  **Call to Action:** Dos botones de navegación:
    - **Botón "Ingresar":** Estilo outline naranja que navega a `/auth/login`
    - **Botón "Registrarse":** Estilo sólido naranja que navega a `/auth/register`
    - Ambos botones usan el color primario `var(--primary)` definido en `globals.css`.

3.  **Diseño de Botones:**
    - **Outline:** Borde naranja, texto naranja, fondo transparente, hover con fondo naranja/10.
    - **Sólido:** Fondo naranja, texto blanco, hover con naranja/90.

4.  **Responsive:** 
    - **Móvil:** Diseño en columna (flex-col), logo arriba, textos centrados, botones apilados verticalmente.
    - **Desktop:** Diseño centrado, elementos espaciados, botones en fila horizontal.
    - Breakpoint: usar `md:` de Tailwind (768px).

5.  **Estructura Atomic Design:**
    - Crear componente `Button` en `components/atoms/` (si no existe) con variants: "outline" | "solid".
    - Crear componente `HeroSection` en `components/organisms/` que agrupe título, subtítulo, logo y botones.
    - Actualizar `src/app/page.tsx` para usar el `HeroSection`.

6.  **Navegación:**
    - Usar componente `<Link>` de Next.js para navegación client-side.
    - Los botones deben tener `href` hacia las rutas correspondientes.

7.  **Accesibilidad:**
    - Botones con textos descriptivos (no solo íconos).
    - Estados de hover y focus visibles.
    - Contraste de colores WCAG AA compliant.

DEINITION OF READY
1. ✅ Wireframe de baja fidelidad del Home aprobado (ver Acceptance Criteria #1-4).
2. ✅ Assets (Logo de la billetera) disponibles - usar `/next.svg` como placeholder (ver Acceptance Criteria #1).

DEFINITION OF DONE (Global Policy):
1. **Formato:** **Prettier** ejecutado en todo el código (`npm run format`).
2. **Linting:** **ESLint** pasando sin errores ni warnings (`npm run lint`).
3. **Typing:** **TypeScript Strict Mode** sin errores (`npm run type-check`).
4. **Cobertura de Pruebas:** >= 85% en líneas, statements, funciones y branches (medido con `nyc`).
5. **Framework de Testing:** Usar **Mocha + Chai + Sinon**.
6. **Tipos de Tests:** Incluir casos positivos, negativos, edge cases, interacciones, estados, accesibilidad y variaciones de props (ver FRONTEND-GUIDELINES.md sección 7.3.2).
7. **Docs:** Componentes documentados con **TSDoc** (props, comportamiento, ejemplos).
8. **Límites:** Ningún archivo excede las 500 líneas.
9. **Validación Local:** Ejecutar `npm run quality:check` antes de commit (format, lint, type-check, test:coverage).
10. **Responsive verificado:** Probar en viewports móvil (375px) y desktop (1024px) mínimo.
11. **Accesibilidad:** Botones navegables con teclado, estados de focus visibles, contraste WCAG AA.

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