function handleLogout(logoutUrl) {
    // 1. Limpiar tokens del cliente (JWT)
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");

    // 2. Redirigir al backend para destruir la sesión de Django
    window.location.href = logoutUrl;
}