from django.db import models, transaction as db_transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
# from .models import Warehouse, InventoryItem, Post, Category

# Create your models here.

# --- Manager para Usuario Personalizado ---

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        """
        Crea y guarda un Usuario con el email, teléfono y contraseña dados.
        """
        if not email:
            raise ValueError('El Email debe ser proporcionado')
        
        email = self.normalize_email(email)
        # Se le asigna un states por defecto
        extra_fields.setdefault('status_id', 1) 
        
        user = self.model(email=email, phone=phone, **extra_fields)
        
        # Django se encarga del HASHING automáticamente con set_password
        user.set_password(password) 
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        """
        Crea y guarda un superusuario.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status_id', 1)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone, password, **extra_fields)


# --- Modelos para Status ---

class Status(models.Model):
    
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Status"

    def __str__(self):
        return self.name

# --- Modelo para usuario ---

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    creation_date = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=20, unique=True)
    
    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    # Campos requeridos por Django Admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Le decimos a Django que use 'email' para el login
    USERNAME_FIELD = 'email'
    
    # Campos requeridos al crear un usuario (ej. 'createsuperuser')
    REQUIRED_FIELDS = ['phone']

    # Asignamos el Manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email

# --- Modelos de Perfiles ---

class Donee(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    first_surname = models.CharField(max_length=255)
    second_surname = models.CharField(max_length=255)
    curp = models.CharField(max_length=18, unique=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.first_surname}"

class Donor(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    first_surname = models.CharField(max_length=255)
    second_surname = models.CharField(max_length=255)
    curp = models.CharField(max_length=18, unique=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.first_surname}"

class Institution(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, unique=True)
    rfc = models.CharField(max_length=13, unique=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
# --- Modelo de publicaciones ---

class Category(models.Model):
    """
    Categorías para las donaciones (ej. Comida, Ropa, Muebles).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    """
    La publicación central (Solicitud o Donación).
    """
    class PostType(models.TextChoices):
        REQUEST = 'REQUEST', 'Solicitud' # Alguien necesita algo
        OFFER = 'OFFER', 'Oferta'       # Alguien ofrece algo

    class PostStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activa'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        COMPLETED = 'COMPLETED', 'Completada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    # --- Campos Principales ---
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT # Evita borrar categorías en uso
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1.0
    )
    
    # --- Campos de Lógica ---
    post_type = models.CharField(
        max_length=10, 
        choices=PostType.choices
    )
    status = models.CharField(
        max_length=20, 
        choices=PostStatus.choices, 
        default=PostStatus.ACTIVE
    )
    
    # --- Banderas de Lógica de Negocio ---
    is_campaign = models.BooleanField(
        default=False, 
        help_text="Marcar si es una campaña masiva (solo Instituciones)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title} por {self.author.email}"


class Transaction(models.Model):
    """
    Registra la interacción de un usuario con un Post.
    """
    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        APPROVED = 'APPROVED', 'Aprobada'
        REJECTED = 'REJECTED', 'Rechazada'
        COMPLETED = 'COMPLETED', 'Completada'

    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    # El usuario que interactúa (NO el autor del post)
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='interactions'
    ) 
    quantity_committed = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=TransactionStatus.choices, 
        default=TransactionStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def approve_and_update_inventory(self, warehouse):
        """
        Aprueba esta transacción y actualiza el inventario 
        en el almacén (warehouse) especificado.
        """

        with db_transaction.atomic():
            
            # No hacer nada si ya estaba aprobada
            if self.status == self.TransactionStatus.APPROVED:
                raise Exception("Esta transacción ya fue aprobada.")

            # Obtener los datos necesarios
            category = self.post.category
            quantity_to_commit = self.quantity_committed
            post_type = self.post.post_type

            # Obtener el item de inventario
            inventory_item, created = InventoryItem.objects.get_or_create(
                warehouse=warehouse,
                category=category,
                defaults={'quantity': 0} # Inicia en 0 si es nuevo
            )

            # Aplicar la logica de negocio 
            if post_type == Post.PostType.OFFER:
                # Si es una OFERTA (donación ENTRANTE), suma al inventario
                inventory_item.quantity += quantity_to_commit
            
            elif post_type == Post.PostType.REQUEST:
                # Si es una SOLICITUD (donación SALIENTE), resta del inventario
                if inventory_item.quantity < quantity_to_commit:
                    raise Exception(f"Stock insuficiente de {category.name} en {warehouse.name}.")
                inventory_item.quantity -= quantity_to_commit
            
            # Guardar los cambios
            inventory_item.save()
            self.status = self.TransactionStatus.APPROVED
            self.save()
            
            # (TODO): Actualizar el estado del Post si ya se completó
            # ... (lógica futura) ...
            
    def __str__(self):
        return f"{self.participant.email} -> {self.post.title}"

# --- Modelos de Inventario ---

class Warehouse(models.Model):
    """
    Representa un almacén o centro de acopio físico.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    # Podríamos asignar un admin (CustomUser) como encargado
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_warehouses"
    )

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    """
    Representa la cantidad de una categoría de producto
    en un almacén específico.
    """
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,
        related_name="inventory_items"
    )
    # Vinculamos el inventario a las Categorías que ya creamos
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, # No borrar una categoría si hay stock
        related_name="inventory_items"
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0
    )
    
    # Fecha de la última actualización de este artículo
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Evita duplicados"
        unique_together = ('warehouse', 'category')

    def __str__(self):
        return f"{self.quantity} de {self.category.name} en {self.warehouse.name}"