"""
Puertos del dominio — Interfaces (contratos) para adaptadores externos.

Define las abstracciones que el dominio necesita sin conocer implementaciones:
- UserRepository: persistencia de usuarios.
- KycVerificationPort: verificación de identidad.
- PasswordHasherPort: hashing de credenciales.
- TokenProviderPort: generación/validación de JWT.
- EventPublisherPort: publicación de eventos de dominio.

Referencia: BACKEND-GUIDELINES.md §2.1, §3.1
"""
