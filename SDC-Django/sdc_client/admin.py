from django.contrib import admin, messages

# Modulos creados por nosotros
from .models import (
    Status, CustomUser, Donee, Donor, Institution,
    Category, Post, Transaction, Warehouse, InventoryItem
)

# Register your models here.


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'manager')
    search_fields = ('name', 'city')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'category', 'quantity', 'last_updated')
    list_filter = ('warehouse', 'category')
    search_fields = ('category__name', 'warehouse__name')

@admin.action(description='Aprobar (Personal - Sin Inventario)')
def approve_personal_transaction(modeladmin, request, queryset):
    """
    Acción: Aprueba transacciones sin afectar inventario.
    """
    pending = queryset.filter(status=Transaction.TransactionStatus.PENDING)
    count = 0
    for transaction in pending:
        try:
            # Llama al nuevo método SIN almacén
            msg = transaction.approve_transaction(warehouse=None)
            count += 1
            messages.success(request, f'"{transaction}": {msg}')
        except Exception as e:
            messages.error(request, f'Error al aprobar "{transaction}": {e}')

@admin.action(description='Aprobar y Mover a/de (Almacén Principal)')
def approve_warehouse_transaction(modeladmin, request, queryset):
    """
    Acción: Aprueba transacciones afectando el inventario.
    Se usa el primer almacén disponible.
    (TODO): Permitir seleccionar almacén en el futuro.
    """
    try:
        warehouse = Warehouse.objects.first()
        if not warehouse:
            raise Exception("No hay almacenes registrados. Cree uno primero.")

        pending = queryset.filter(status=Transaction.TransactionStatus.PENDING)

        for transaction in pending:
            try:
                # Llama al nuevo método CON el almacén
                msg = transaction.approve_transaction(warehouse=warehouse)
                messages.success(request, f'"{transaction}": {msg}')
            except Exception as e:
                messages.error(request, f'Error al aprobar "{transaction}": {e}')

    except Exception as e:
        messages.error(request, f'Error general: {e}')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'participant', 'status', 'quantity_committed', 'created_at')
    list_filter = ('status', 'post__category')
    search_fields = ('post__title', 'participant__email')

    # agregar las acciones personalizadas
    actions = [approve_personal_transaction, approve_warehouse_transaction]


admin.site.register(CustomUser)
admin.site.register(Status)
admin.site.register(Donee)
admin.site.register(Donor)
admin.site.register(Institution)
admin.site.register(Category)
admin.site.register(Post)
# admin.site.register(Transaction)