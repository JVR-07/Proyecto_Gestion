from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth import authenticate, login # Para Login
from django.contrib.auth.decorators import login_required # Decorador para proteger vistas
from django.http import JsonResponse
import json

# --- FORMULARIOS ---
from .forms import PersonRegistrationForm, InstitutionRegistrationForm, PostForm
# --- MODELOS ---
from .models import CustomUser, Donee, Donor, Institution, Post, Transaction

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
        # --- Pasar 'user=request.user' al formulario ---
        form = PostForm(request.POST, user=request.user)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            redirect_url = 'home' 

            try:
                if hasattr(request.user, 'donee'):
                    # REGLA: Donatario.
                    post.post_type = Post.PostType.REQUEST
                    post.is_campaign = False 
                    redirect_url = 'donee_feed'

                elif hasattr(request.user, 'donor'):
                    # REGLA: Donador.
                    post.post_type = Post.PostType.OFFER
                    post.is_campaign = False
                    redirect_url = 'donor_feed'

                elif hasattr(request.user, 'institution'):
                    # REGLA: Institución.
                    redirect_url = 'institution_feed'
                
                else:
                    messages.error(request, 'Error: Tu perfil de usuario no está completo.')
                    return redirect('home')

                post.save() # Guardar el objeto 'post' en la BBDD
                messages.success(request, '¡Publicación creada con éxito!')
                return redirect(redirect_url) 

            except Exception as e:
                form.add_error(None, f"Error al procesar el tipo de usuario: {e}")

    else:
        form = PostForm(user=request.user)

    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)

@login_required
def donee_feed(request):
    my_requests = Post.objects.filter(
        author=request.user, 
        post_type=Post.PostType.REQUEST
    ).order_by('-created_at')
    
    available_offers = Post.objects.filter(
        post_type=Post.PostType.OFFER, 
        status=Post.PostStatus.ACTIVE
    ).exclude(author=request.user).order_by('-created_at')

    context = {
        'my_posts': my_requests,
        'feed_posts': available_offers,
        'feed_title': 'Ofertas Disponibles'
    }
    return render(request, 'posts/donee_feed.html', context)


@login_required
def donor_feed(request):
    my_offers = Post.objects.filter(
        author=request.user, 
        post_type=Post.PostType.OFFER
    ).order_by('-created_at')

    available_requests = Post.objects.filter(
        post_type=Post.PostType.REQUEST, 
        status=Post.PostStatus.ACTIVE
    ).exclude(author=request.user).order_by('-created_at')

    context = {
        'my_posts': my_offers,
        'feed_posts': available_requests,
        'feed_title': 'Solicitudes de Ayuda'
    }
    return render(request, 'posts/donor_feed.html', context)


@login_required
def institution_feed(request):
    my_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    all_other_posts = Post.objects.filter(
        status=Post.PostStatus.ACTIVE
    ).exclude(author=request.user).order_by('-created_at')

    context = {
        'my_posts': my_posts,
        'feed_posts': all_other_posts,
        'feed_title': 'Actividad de la Comunidad'
    }
    return render(request, 'posts/institution_feed.html', context)

@login_required
def create_transaction(request, post_id):
    # Solo permitimos peticiones POST
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        # Evitar que el autor interactúe con su propio post
        if post.author == request.user:
            messages.error(request, 'No puedes interactuar con tu propia publicación.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        try:
            quantity = request.POST.get('quantity_committed')
            if not quantity or float(quantity) <= 0:
                messages.error(request, 'Debes proveer una cantidad válida.')
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # Crear la transacción en estado PENDIENTE
            Transaction.objects.create(
                post=post,
                participant=request.user,
                quantity_committed=quantity,
                status=Transaction.TransactionStatus.PENDING 
            )
            messages.success(request, '¡Tu interés ha sido registrado! Un administrador lo revisará.')
        
        except IntegrityError:
            messages.warning(request, 'Ya tienes una interacción pendiente en esta publicación.')
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    # Redirigir de vuelta a la página de donde venía
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# --- Lógica de Registro (Backend) ---

def register(request):
    person_form = PersonRegistrationForm()
    institution_form = InstitutionRegistrationForm()

    if request.method == 'POST':
        # --- Lógica de Registro de Persona ---
        if 'person_curp' in request.POST:
            person_form = PersonRegistrationForm(request.POST)
            if person_form.is_valid():
                data = person_form.cleaned_data
                
                # Usamos una transacción para asegurar que ambos se creen
                try:
                    with transaction.atomic():
                        # Crear el CustomUser
                        user = CustomUser.objects.create_user(
                            email=data['person_email'],
                            phone=data['person_phone'],
                            password=data['person_password']
                        )
                        
                        # Crear el Perfil (Donee o Donor)
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
                            redirect_url = 'donee_feed'
                        else: # 'donor'
                            Donor.objects.create(**profile_data)
                            redirect_url = 'donor_feed'

                    messages.success(request, '¡Registro exitoso! Por favor, inicia sesión.')
                    return redirect('auth') # Redirigir a la página de login

                except Exception as e:
                    # Captura errores
                    messages.error(request, f'Error al crear el usuario: {e}')

        # --- Lógica de Registro de Institución ---
        elif 'institution_rfc' in request.POST:
            institution_form = InstitutionRegistrationForm(request.POST)
            if institution_form.is_valid():
                data = institution_form.cleaned_data

                try:
                    with transaction.atomic():
                        # Crear el CustomUser para la institución
                        user = CustomUser.objects.create_user(
                            email=data['institution_email'],
                            phone=data['institution_rfc'], # Usar RFC como fono temporal
                            password=data['institution_password']
                        )
                        
                        # Crear el Perfil de Institución
                        Institution.objects.create(
                            user=user,
                            name=data['institution_name'],
                            rfc=data['institution_rfc'],
                            city=data['institution_city'],
                            state=data['institution_state'],
                            address=data['institution_address']
                        )
                    
                    messages.success(request, '¡Registro de institución exitoso! Por favor, inicia sesión.')
                    return redirect('auth') # Redirigir a la página de login

                except Exception as e:
                    messages.error(request, f'Error al crear la institución: {e}')

    # Si es GET o el formulario no es válido, renderiza la página con los errores
    context = {
        'person_form': person_form,
        'institution_form': institution_form,
    }
    return render(request, 'login/register.html', context)


# --- Lógica de Login (Backend) con JWT ---

@api_view(['POST']) 
@permission_classes([AllowAny]) 
def api_login_view(request):
    
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return JsonResponse({'error': 'Email y contraseña requeridos'}, status=400)

    # Autenticar al usuario
    user = authenticate(request, email=email, password=password)

    if user is not None:
        # Crear la sesión en el servidor para Django
        login(request, user) 
        
        # Generar los tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Determinar el tipo de usuario y la URL de redirección
        user_type = 'unknown'
        redirect_url = '/'
        
        if hasattr(user, 'donor'):
            user_type = 'donor'
            redirect_url = '/donor_feed'
        elif hasattr(user, 'donee'):
            user_type = 'donee'
            redirect_url = '/donee_feed'
        elif hasattr(user, 'institution'):
            user_type = 'institution'
            redirect_url = '/institution_feed'
        
        # Devolver la respuesta JSON al frontend
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
        # Autenticación fallida
        return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    
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
        
        user_type = 'unknown'
        redirect_url = '/'

        try:
            # Intenta acceder al perfil de Donador.
            if user.donor:
                user_type = 'donor'
                redirect_url = '/donor_feed'
        except Donor.DoesNotExist:
            # Si da error, no es un Donador. Sigue al siguiente.
            try:
                # Intenta acceder al perfil de Donatario.
                if user.donee:
                    user_type = 'donee'
                    redirect_url = '/donee_feed'
            except Donee.DoesNotExist:
                # Si da error, no es Donatario. Sigue al siguiente.
                try:
                    # Intenta acceder al perfil de Institución.
                    if user.institution:
                        user_type = 'institution'
                        redirect_url = '/institution_feed'
                except Institution.DoesNotExist:
                    # Si da error, no es ninguno.
                    pass
        except Exception as e:
            # Captura cualquier otro error (ej. si olvidaste importar un modelo)
            return JsonResponse({'error': f'Error de servidor inesperado: {e}'}, status=500)
        
        # 4. Devuelve la respuesta exitosa
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
        # Autenticación fallida (contraseña incorrecta)
        return JsonResponse({'error': 'Credenciales inválidas'}, status=401)