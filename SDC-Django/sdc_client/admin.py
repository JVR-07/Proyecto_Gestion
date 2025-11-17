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

@admin.action(description='Aprobar transacciones y actualizar inventario (Almacén Principal)')
def approve_selected_transactions(modeladmin, request, queryset):
    """
    Acción de Admin para aprobar transacciones pendientes.
    """
    # Simplificación: Asumimos que todo va al primer almacén.
    # TODO: Crear una página intermedia para que el admin ELIJA el almacén.
    try:
        warehouse = Warehouse.objects.first()
        if not warehouse:
            raise Exception("No hay almacenes registrados.")
        
        approved_count = 0
        # Solo intentar aprobar las que están PENDIENTES
        pending_transactions = queryset.filter(status=Transaction.TransactionStatus.PENDING)
        
        for transaction in pending_transactions:
            try:
                transaction.approve_and_update_inventory(warehouse)
                approved_count += 1
            except Exception as e:
                # Reportar error por transacción
                messages.error(request, f'Error al aprobar "{transaction}": {e}')
        
        if approved_count > 0:
            messages.success(request, f'{approved_count} transacciones aprobadas y añadidas a "{warehouse.name}".')

    except Exception as e:
        messages.error(request, f'Error general: {e}')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'participant', 'status', 'quantity_committed', 'created_at')
    list_filter = ('status', 'post__category')
    search_fields = ('post__title', 'participant__email')
    
    # Añadimos la acción al admin
    actions = [approve_selected_transactions]


admin.site.register(CustomUser)
admin.site.register(Status)
admin.site.register(Donee)
admin.site.register(Donor)
admin.site.register(Institution)
admin.site.register(Category)
admin.site.register(Post)
# admin.site.register(Transaction)