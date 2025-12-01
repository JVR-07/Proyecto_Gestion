from django.contrib import admin, messages
from django.utils import timezone

# Modulos creados por nosotros
from .models import (
    Status, CustomUser, Donee, Donor, Institution,
    Category, Post, Transaction, Warehouse, InventoryItem,
    MeasurementUnit, Report
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

@admin.action(description='VALIDAR Reporte (Eliminar Publicación)')
def validate_report_and_delete_post(modeladmin, request, queryset):
    """
    Si el reporte es válido:
    1. Marca el reporte como VALIDATED.
    2. Marca la publicación asociada como CANCELLED (Soft Delete).
    """
    for report in queryset:
        if report.status == Report.ReportStatus.PENDING:
            post = report.post
            post.status = Post.PostStatus.CANCELLED
            post.save()
            
            report.status = Report.ReportStatus.VALIDATED
            report.resolved_at = timezone.now()
            report.save()
    
    messages.success(request, "Reportes validados. Las publicaciones asociadas han sido canceladas.")

@admin.action(description='RECHAZAR Reporte (Conservar Publicación)')
def reject_report(modeladmin, request, queryset):
    """
    Si el reporte es falso/spam:
    1. Marca el reporte como REJECTED.
    2. No toca la publicación.
    """
    queryset.update(status=Report.ReportStatus.REJECTED, resolved_at=timezone.now())
    messages.info(request, "Reportes rechazados. Las publicaciones permanecen activas.")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('reason', 'post__title', 'reporter__email')
    actions = [validate_report_and_delete_post, reject_report]

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