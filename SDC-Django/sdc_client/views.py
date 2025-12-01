from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # Decorador para proteger vistas
from django.http import JsonResponse
import json
from decimal import Decimal

# --- FORMULARIOS ---
from .forms import PersonRegistrationForm, InstitutionRegistrationForm, PostForm, ReportForm
# --- MODELOS ---
from .models import CustomUser, Donee, Donor, Institution, Post, Transaction, InventoryItem, Warehouse, Report

# Importaciones para JWT y Vistas de API (para el login)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


# --- Vistas de Páginas (Frontend) ---

def home(request):
    return render(request, 'landing/home.html')

def login_page(request):
    return render(request, 'login/login.html')

def auth(request):
    return render(request, 'login/auth.html')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            redirect_url = 'home' 
            try:
                try:
                    if request.user.institution:
                        redirect_url = 'institution_feed'
                        
                        if post.post_type == Post.PostType.OFFER and post.warehouse:
                            inventory_item = InventoryItem.objects.get(
                                warehouse=post.warehouse, 
                                category=post.category
                            )
                            inventory_item.quantity -= post.quantity
                            inventory_item.save()
                            
                            messages.info(request, f"Se han reservado {post.quantity} del almacén '{post.warehouse.name}'.")

                except Institution.DoesNotExist:
                        messages.error(request, 'Error: Tu perfil de usuario no está completo.')
                        return redirect('home')

                post.save() 
                messages.success(request, '¡Publicación creada con éxito!')
                return redirect(redirect_url) 
            
            except InventoryItem.DoesNotExist:
                form.add_error(None, "Error crítico: No se encontró el inventario para reservar.")
            except Exception as e:
                form.add_error(None, f"Error al procesar la publicación: {e}")
    else:
        form = PostForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        messages.error(request, "No tienes permiso para editar esta publicación.")
        return redirect('home')
    
    is_readonly = post.status in [Post.PostStatus.CANCELLED, Post.PostStatus.COMPLETED]

    if request.method == 'POST':
        if is_readonly:
            messages.error(request, "No puedes editar una publicación cerrada.")
            return redirect('home')
        
        form = PostForm(request.POST, instance=post, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '¡Publicación actualizada correctamente!')
                
                if hasattr(request.user, 'institution'):
                    return redirect('institution_feed')
                elif hasattr(request.user, 'donor'):
                    return redirect('donor_feed')
                elif hasattr(request.user, 'donee'):
                    return redirect('donee_feed')
                return redirect('home')
                
            except Exception:
                messages.error(request, "No se pudieron guardar los cambios debido a un error inesperado.")
    else:
        form = PostForm(instance=post, user=request.user)

    context = {
        'form': form,
        'is_edit': True,
        'is_readonly': is_readonly,
        'post_status': post.get_status_display()
    }
    return render(request, 'posts/create_post.html', context)

@login_required
def close_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        messages.error(request, "No tienes permiso para cerrar esta publicación.")
        return redirect('home')
    
    try:
        with transaction.atomic():
            if post.post_type == Post.PostType.OFFER and hasattr(request.user, 'institution') and post.warehouse:
                remaining = post.quantity_remaining
                if remaining > 0:
                    inventory_item = InventoryItem.objects.get(
                        warehouse=post.warehouse,
                        category=post.category
                    )
                    inventory_item.quantity += remaining
                    inventory_item.save()
                    messages.info(request, f"Se han devuelto {remaining} unidades al inventario de '{post.warehouse.name}'.")

            pending_transactions = post.transactions.filter(status=Transaction.TransactionStatus.PENDING)
            count_cancelled = pending_transactions.count()
            pending_transactions.update(status=Transaction.TransactionStatus.REJECTED)
            
            post.status = Post.PostStatus.CANCELLED
            post.save()
            
            if count_cancelled > 0:
                messages.warning(request, f"Publicación cerrada. {count_cancelled} solicitudes pendientes fueron rechazadas automáticamente.")
            else:
                messages.success(request, "Publicación cerrada correctamente.")

    except Exception as e:
        messages.error(request, f"Error al cerrar la publicación: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def donee_feed(request):
    if not hasattr(request.user, 'donee'):
        messages.error(request, "No tienes permisos para ver el panel de Donatarios.")
        return redirect('home')

    my_requests = Post.objects.filter(author=request.user, post_type=Post.PostType.REQUEST).order_by('-created_at')
    available_offers = Post.objects.filter(post_type=Post.PostType.OFFER, status=Post.PostStatus.ACTIVE).exclude(author=request.user).order_by('-created_at')
    context = {
        'my_posts': my_requests,
        'feed_posts': available_offers,
        'feed_title': 'Ofertas Disponibles'
    }
    return render(request, 'posts/donee_feed.html', context)


@login_required
def donor_feed(request):
    if not hasattr(request.user, 'donor'):
        messages.error(request, "No tienes permisos para ver el panel de Donadores.")
        return redirect('home')

    my_offers = Post.objects.filter(author=request.user, post_type=Post.PostType.OFFER).order_by('-created_at')
    available_requests = Post.objects.filter(post_type=Post.PostType.REQUEST, status=Post.PostStatus.ACTIVE).exclude(author=request.user).order_by('-created_at')
    context = {
        'my_posts': my_offers,
        'feed_posts': available_requests,
        'feed_title': 'Solicitudes de Ayuda'
    }
    return render(request, 'posts/donor_feed.html', context)


@login_required
def institution_feed(request):
    if not hasattr(request.user, 'institution'):
        messages.error(request, "No tienes permisos para ver el panel de Instituciones.")
        return redirect('home')

    my_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    all_other_posts = Post.objects.filter(status=Post.PostStatus.ACTIVE).exclude(author=request.user).order_by('-created_at')
    context = {
        'my_posts': my_posts,
        'feed_posts': all_other_posts,
        'feed_title': 'Actividad de la Comunidad'
    }
    return render(request, 'posts/institution_feed.html', context)

@login_required
def create_transaction(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        if post.author == request.user:
            messages.error(request, 'No puedes interactuar con tu propia publicación.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        try:
            # Validar la cantidad enviada
            quantity_str = request.POST.get('quantity_committed')
            if not quantity_str:
                messages.error(request, 'Debes proveer una cantidad.')
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            
            quantity_committed = Decimal(quantity_str)

            if quantity_committed <= 0:
                messages.error(request, 'La cantidad debe ser mayor a cero.')
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # Usar la nueva propiedad para verificar el stock
            quantity_remaining = post.quantity_remaining.quantize(Decimal('0.01'))

            if quantity_committed > quantity_remaining:
                messages.error(request, f"La cantidad ({quantity_committed}) supera lo restante ({quantity_remaining}).")
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # Crear la transacción
            Transaction.objects.create(
                post=post,
                participant=request.user,
                quantity_committed=quantity_committed,
                status=Transaction.TransactionStatus.PENDING 
            )
            messages.success(request, '¡Tu interés ha sido registrado! Un administrador lo revisará.')
        
        except IntegrityError:
            messages.warning(request, 'Ya tienes una interacción pendiente en esta publicación.')
        except Exception:
            messages.error(request, 'No se pudo procesar tu solicitud. Por favor, verifica los datos e inténtalo de nuevo.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))


# --- Lógica de Registro (Backend) ---
def register(request):
    person_form = PersonRegistrationForm()
    institution_form = InstitutionRegistrationForm()
    if request.method == 'POST':
        if 'person_curp' in request.POST:
            person_form = PersonRegistrationForm(request.POST)
            if person_form.is_valid():
                data = person_form.cleaned_data
                try:
                    with transaction.atomic():
                        user = CustomUser.objects.create_user(
                            email=data['person_email'],
                            phone=data['person_phone'],
                            password=data['person_password']
                        )
                        profile_data = {
                            'user': user,
                            'first_name': data['person_first_name'],
                            'middle_name': data['person_middle_name'],
                            'first_surname': data['person_first_surname'],
                            'second_surname': data['person_second_surname'],
                            'curp': data['person_curp'],
                            'city': data['person_city'],
                            'state': data['person_state']
                        }
                        if data['user_type'] == 'donee':
                            Donee.objects.create(**profile_data)
                        else: # 'donor'
                            Donor.objects.create(**profile_data)
                    messages.success(request, '¡Registro exitoso! Por favor, inicia sesión.')
                    return redirect('auth')
                except Exception:
                    messages.error(request, 'No se pudo completar el registro. Verifica que el correo no esté registrado.')
        elif 'institution_rfc' in request.POST:
            institution_form = InstitutionRegistrationForm(request.POST)
            if institution_form.is_valid():
                data = institution_form.cleaned_data
                try:
                    with transaction.atomic():
                        user = CustomUser.objects.create_user(
                            email=data['institution_email'],
                            phone=data['institution_rfc'],
                            password=data['institution_password']
                        )
                        Institution.objects.create(
                            user=user,
                            name=data['institution_name'],
                            rfc=data['institution_rfc'],
                            city=data['institution_city'],
                            state=data['institution_state'],
                            address=data['institution_address']
                        )
                    messages.success(request, '¡Registro de institución exitoso! Por favor, inicia sesión.')
                    return redirect('auth')
                except Exception:
                    messages.error(request, 'Error al registrar la institución. Es posible que el RFC o correo ya existan.')
    context = {
        'person_form': person_form,
        'institution_form': institution_form,
    }
    return render(request, 'login/register.html', context)

@login_required
def institution_list_view(request):
    """
    Muestra una lista de todas las Instituciones registradas
    con sus estadísticas clave.
    """
    institutions = Institution.objects.all()
    
    stats_data = []
    
    for inst in institutions:
        # 1. Total Donado (Ofertas aprobadas)
        # Buscamos transacciones donde el post sea de esta institución y tipo OFFER
        donated_qty = Transaction.objects.filter(
            post__author=inst.user,
            post__post_type=Post.PostType.OFFER,
            status=Transaction.TransactionStatus.APPROVED
        ).aggregate(total=Sum('quantity_committed'))['total'] or 0
        
        # 2. Campañas Activas (Requests que son campañas)
        active_campaigns = Post.objects.filter(
            author=inst.user,
            post_type=Post.PostType.REQUEST,
            is_campaign=True,
            status=Post.PostStatus.ACTIVE
        ).count()

        # 3. Inventario Total (Suma de cantidades en sus almacenes)
        # Usamos la relación inversa 'warehouses' -> 'inventory_items'
        total_inventory = InventoryItem.objects.filter(
            warehouse__in=inst.warehouses.all()
        ).aggregate(total=Sum('quantity'))['total'] or 0

        stats_data.append({
            'institution': inst,
            'donated_qty': donated_qty,
            'active_campaigns': active_campaigns,
            'total_inventory': total_inventory
        })

    context = {
        'stats_data': stats_data
    }
    return render(request, 'stats/institution_list.html', context)

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            messages.success(request, "Tu reporte ha sido enviado a los administradores.")
        else:
            messages.error(request, "Error al enviar el reporte. Revisa el motivo.")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# --- Lógica de Login (Backend) con JWT ---
@api_view(['POST']) 
@permission_classes([AllowAny]) 
def api_login_view(request):
    
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return JsonResponse({'error': 'Email y contraseña requeridos'}, status=400)

    user = authenticate(request, email=email, password=password)

    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        
        user_type = 'admin' # Valor por defecto
        redirect_url = '/admin/' # Valor por defecto

        try:
            if user.donor:
                user_type = 'donor'
                redirect_url = '/donor_feed'
        except Donor.DoesNotExist:
            try:
                if user.donee:
                    user_type = 'donee'
                    redirect_url = '/donee_feed'
            except Donee.DoesNotExist:
                try:
                    if user.institution:
                        user_type = 'institution'
                        redirect_url = '/institution_feed'
                except Institution.DoesNotExist:
                    pass # Se queda con los valores de 'admin'
        except Exception:
            return JsonResponse({'error': 'Ocurrió un problema técnico al verificar tu cuenta.'}, status=500)
        
        return JsonResponse({
            'message': 'Login exitoso',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'user_type': user_type,
                'redirect_url': redirect_url
            }
        }, status=200)
    else:
        return JsonResponse({'error': 'Credenciales inválidas'}, status=401)

def sign_out(request):
    """
    Cierra la sesión del usuario en el servidor y redirige.
    """
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')