document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            
            showFloatingToast("¡Bienvenido! Redirigiendo...", "success");
            
            setTimeout(() => {
                window.location.href = data.user.redirect_url;
            }, 1000);
        } else {
            showFloatingToast(data.error || 'Error al iniciar sesión.', 'error');
        }

    } catch (error) {
        console.error('Error de red:', error);
        showFloatingToast('Error de conexión. Verifica tu internet.', 'error');
    }
});