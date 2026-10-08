# POS Multi-sucursal con Django

Sistema de punto de venta robusto con soporte multi-sucursal, roles y preparación para producción.

## Funcionalidades incluidas
- Gestión de productos, categorías y clientes.
- Proceso de ventas con actualización transaccional de inventario.
- Alertas de stock bajo en dashboard.
- Métodos de pago: efectivo, tarjeta y transferencia.
- Reportería diaria, mensual y por producto en capa de servicios.
- Historial de transacciones por modelo `Sale`.
- Cierre de caja con validación de diferencia (`variance`).
- Soporte multi-sucursal con modelo `Branch` y usuario asociado.

## Arquitectura
- `apps/core`: usuarios, roles y sucursales.
- `apps/pos`: productos, inventario, ventas, clientes y cierre.
- `apps/payments`: integración base con pasarelas externas.
- `apps/reports`: servicios de agregación para reportes.

## Instalación
1. Crear virtualenv e instalar dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Inicializar DB de desarrollo:
   ```bash
   ./scripts/init_db.sh
   ```
3. Crear superusuario y ejecutar:
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

## Configuración de entornos
- Desarrollo: `pos_project.settings.development` (SQLite).
- Producción: `pos_project.settings.production` (PostgreSQL + cookies seguras).

## Integraciones de pago (especificación técnica)
`apps/payments/services.py` define `PaymentGatewayService` como adaptador.
Para producción:
1. Implementar proveedor real (Stripe/Adyen/MercadoPago) con SDK oficial.
2. Tokenizar tarjeta en frontend y enviar token al backend (nunca PAN completo).
3. Usar idempotency keys por venta para evitar doble cargo.
4. Guardar `gateway_reference`, estado y payload en tabla de auditoría.
5. Activar webhooks firmados para confirmar/cancelar pagos asíncronos.

## Multi-sucursal (especificación técnica)
- Cada `Product` y `Sale` pertenece a `Branch`.
- El usuario opera sobre su `branch` asignada.
- Para datos centralizados, desplegar única base PostgreSQL con índices por `branch_id`.
- Para escalado horizontal, usar particionamiento lógico por sucursal y réplicas de lectura para reportes.

## Calidad y pruebas
- Manejo transaccional con `transaction.atomic` y `select_for_update`.
- Validaciones de stock y cantidad.
- Logging centralizado configurable.
- Test unitario crítico en `apps/pos/tests.py`.

