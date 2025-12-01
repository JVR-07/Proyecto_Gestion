from django.contrib import admin, messages

# Modulos creados por nosotros
from .models import (
    Status, CustomUser, Donee, Donor, Institution,
    Category, Post, Transaction, Warehouse, InventoryItem,
    MeasurementUnit
)

# Register your models here.


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'manager')
    search_fields = ('name', 'city')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'rfc', 'city')
    search_fields = ('name', 'rfc')
    filter_horizontal = ('warehouses',)

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

@admin.action(description='Aprobar y Mover a/de Almacén (Automático)')
def approve_warehouse_transaction(modeladmin, request, queryset):
    """
    Acción: Aprueba transacciones afectando el inventario.
    Usa el almacén definido en el Post de la Institución.
    """
    pending = queryset.filter(status=Transaction.TransactionStatus.PENDING)
    
    success_count = 0
    for transaction in pending:
        try:
            target_warehouse = transaction.post.warehouse
            
            if not target_warehouse:
                raise Exception("El post de esta transacción no tiene un almacén asignado.")

            msg = transaction.approve_transaction(warehouse=target_warehouse)
            messages.success(request, f'"{transaction}": {msg}')
            success_count += 1
            
        except Exception as e:
            messages.error(request, f'Error al aprobar "{transaction}": {e}')

@admin.action(description='Rechazar transacciones seleccionadas')
def reject_transactions(modeladmin, request, queryset):
    """
    Marca las transacciones como rechazadas.
    Esto libera la cantidad 'pendiente' en la publicación.
    """
    updated_count = queryset.update(status=Transaction.TransactionStatus.REJECTED)
    messages.success(request, f"{updated_count} transacciones han sido rechazadas.")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'participant', 'status', 'quantity_committed', 'created_at')
    list_filter = ('status', 'post__category')
    search_fields = ('post__title', 'participant__email')

    actions = [approve_personal_transaction, approve_warehouse_transaction, reject_transactions]

admin.site.register(CustomUser)
admin.site.register(Status)
admin.site.register(Donee)
admin.site.register(Donor)
# admin.site.register(Institution)
admin.site.register(Category)
admin.site.register(Post)
# admin.site.register(Transaction)

@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'max_limit_normal')
    search_fields = ('name', 'symbol')