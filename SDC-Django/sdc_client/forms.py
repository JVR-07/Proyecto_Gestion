import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Category, MeasurementUnit, Warehouse, InventoryItem

# --- Funciones de Validación Reutilizables ---

def validate_no_numbers(value):
    """Valida que el campo no contenga números."""
    if any(char.isdigit() for char in value):
        raise ValidationError('Este campo no puede contener números.')

def validate_phone(value):
    """Valida que el campo solo contenga números."""
    if not value.isdigit():
        raise ValidationError('El teléfono debe contener solo números.')

def validate_curp(value):
    """Valida el formato de CURP."""
    curp_regex = r'^[A-Za-z]{4}\d{6}[HhMm]{1}[A-Za-z]{2}[A-Za-z]{3}[A-Za-z0-9]{2}$'
    if not re.match(curp_regex, value.upper()):
        raise ValidationError('El formato del CURP no es válido.')

def validate_rfc(value):
    """Valida el formato de RFC."""
    rfc_regex = r'^[A-Z&Ñ]{3,4}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[A-Z0-9]{3}$'
    if not re.match(rfc_regex, value.upper()):
        raise ValidationError('El formato del RFC no es válido.')

# --- Formularios de Registro ---

class PersonRegistrationForm(forms.Form):
    person_first_name = forms.CharField(label='Primer nombre', max_length=100, validators=[validate_no_numbers])
    person_middle_name = forms.CharField(label='Segundo nombre', max_length=100, required=False, validators=[validate_no_numbers])
    person_first_surname = forms.CharField(label='Primer apellido', max_length=100, validators=[validate_no_numbers])
    person_second_surname = forms.CharField(label='Segundo apellido', max_length=100, validators=[validate_no_numbers])
    person_curp = forms.CharField(label='CURP', max_length=18, validators=[validate_curp])
    person_city = forms.CharField(label='Ciudad', max_length=100)
    person_state = forms.CharField(label='Estado', max_length=100)
    person_email = forms.EmailField(label='Correo electrónico')
    person_phone = forms.CharField(label='Teléfono', max_length=15, validators=[validate_phone])
    person_password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_person_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    user_type = forms.ChoiceField(label='Tipo de usuario', choices=[('donee', 'Donatario'), ('donor', 'Donador')])

    def clean_person_email(self):
        """Valida que el email no esté ya en uso."""
        email = self.cleaned_data.get('person_email')
        return email

    def clean(self):
        """Valida que las contraseñas coincidan."""
        cleaned_data = super().clean()
        password = cleaned_data.get("person_password")
        confirm_password = cleaned_data.get("confirm_person_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_person_password', "Las contraseñas no coinciden.")
        
        # Validación de seguridad de contraseña
        if password:
            if len(password) < 8:
                self.add_error('person_password', 'La contraseña debe tener al menos 8 caracteres.')
            if not re.search(r'[A-Z]', password):
                self.add_error('person_password', 'La contraseña debe contener al menos una mayúscula.')
            if not re.search(r'[0-9]', password):
                self.add_error('person_password', 'La contraseña debe contener al menos un número.')
        
        return cleaned_data

class InstitutionRegistrationForm(forms.Form):
    institution_name = forms.CharField(label='Nombre de la institución', max_length=255)
    institution_rfc = forms.CharField(label='RFC', max_length=13, validators=[validate_rfc])
    institution_city = forms.CharField(label='Ciudad', max_length=100)
    institution_state = forms.CharField(label='Estado', max_length=100)
    institution_address = forms.CharField(label='Dirección', max_length=255)
    institution_email = forms.EmailField(label='Correo institucional')
    institution_password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_institution_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean_institution_email(self):
        """Valida que el email no esté ya en uso."""
        email = self.cleaned_data.get('institution_email')
        return email

    def clean(self):
        """Valida que las contraseñas coincidan."""
        cleaned_data = super().clean()
        password = cleaned_data.get("institution_password")
        confirm_password = cleaned_data.get("confirm_institution_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_institution_password', "Las contraseñas no coinciden.")
        
       # Validación de seguridad de contraseña
        if password:
            if len(password) < 8:
                self.add_error('institution_password', 'La contraseña debe tener al menos 8 caracteres.')
            if not re.search(r'[A-Z]', password):
                self.add_error('institution_password', 'La contraseña debe contener al menos una mayúscula.')
            if not re.search(r'[0-9]', password):
                self.add_error('institution_password', 'La contraseña debe contener al menos un número.')
        
        return cleaned_data

# --- Formulario de Publicaciones ---

class PostForm(forms.ModelForm):
    """
    Formulario para crear nuevas publicaciones.
    Muestra campos adicionales si el usuario es una Institución.
    """
    # Campo para tipo de publicación
    post_type = forms.ChoiceField(
        label="Tipo de Publicación",
        choices=Post.PostType.choices,
        widget=forms.RadioSelect, # Usar radio buttons es más claro
        required=True
    )
    
    # Checkbox para campañas masivas
    is_campaign = forms.BooleanField(
        label="¿Es una campaña masiva?",
        help_text="Marca esta casilla si es una solicitud o donación a gran escala.",
        required=False # No es obligatorio
    )

    # El campo de categoría que ya teníamos
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Categoría",
        empty_label="Selecciona una categoría",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para unidad de medida
    unit = forms.ModelChoiceField(
        queryset=MeasurementUnit.objects.all(),
        label="Unidad de Medida",
        empty_label="Selecciona una unidad",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para almacén (solo para Instituciones)
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.none(),
        label="Almacén",
        required=False,
        empty_label="Selecciona un almacén",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Post
        fields = [
            'post_type',
            'is_campaign',
            'title', 
            'description', 
            'category', 
            'quantity',
            'unit',
            'warehouse',
        ]
        labels = {
            'title': 'Título de la publicación',
            'description': 'Descripción ',
            'quantity': 'Cantidad',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Ej. Ropa de invierno para niños'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describo a detalle...', 'rows': 4}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Ej. 10', 'min': '0.01'}),
        }

    # --- Lógica Dinámica en __init__ ---
    def __init__(self, *args, **kwargs):
        # Extraemos el 'user' que la vista nos pasará
        user = kwargs.pop('user', None)
        
        super().__init__(*args, **kwargs)
        
        # Lógica de queryset de categoría
        if 'Category' in globals():
            self.fields['category'].queryset = Category.objects.all()
        else:
            self.fields['category'].queryset = Category.objects.none()

        # --- Lógica de visibilidad por ROL ---
        is_institution = False
        if user is not None and hasattr(user, 'institution'):
            is_institution = True

            self.fields['warehouse'].queryset = user.institution.warehouses.all()
        
        # Si el usuario NO es una institución, eliminamos los campos
        if not is_institution:
            del self.fields['post_type']
            del self.fields['is_campaign']
            del self.fields['warehouse']
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit = cleaned_data.get('unit')
        is_campaign = cleaned_data.get('is_campaign')
        post_type = cleaned_data.get('post_type')
        warehouse = cleaned_data.get('warehouse')
        category = cleaned_data.get('category')
        
        # Validación de Límite
        if quantity and unit:
            limit = unit.max_limit_normal
            if not is_campaign and quantity > limit:
                msg = f"El límite para {unit.name} es de {limit} {unit.symbol}. (Intentaste publicar: {quantity})"
                self.add_error('quantity', msg)
                
                if 'is_campaign' in self.fields:
                     self.add_error('is_campaign', "Para cantidades mayores, una Institución debe marcar '¿Es una campaña masiva?'.")

        # Validación de Stock en Almacén
        if post_type == Post.PostType.OFFER and warehouse and category and quantity:
            try:
                inventory_item = InventoryItem.objects.get(warehouse=warehouse, category=category)
                
                if inventory_item.quantity < quantity:
                    msg = f"Stock insuficiente en '{warehouse.name}'. Disponible: {inventory_item.quantity} {category.name}."
                    self.add_error('quantity', msg)
                    self.add_error('warehouse', "Selecciona otro almacén o ajusta la cantidad.")
            
            except InventoryItem.DoesNotExist:
                msg = f"No hay stock de '{category.name}' en el almacén '{warehouse.name}'."
                self.add_error('category', msg)
                self.add_error('warehouse', "Este almacén no tiene este producto.")

        return cleaned_data