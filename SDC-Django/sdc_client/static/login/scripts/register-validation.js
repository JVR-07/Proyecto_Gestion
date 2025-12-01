document.addEventListener("DOMContentLoaded", () => {
    console.log("Register Validation Script Loaded");   
    // --- Expresiones Regulares ---
    const REGEX = {
        email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        // CURP: 4 letras, 6 números, H/M, 2 letras entidad, 3 consonantes, 1 homoclave, 1 dígito verificador
        curp: /^[A-Z]{1}[AEIOU]{1}[A-Z]{2}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[HM]{1}(AS|BC|BS|CC|CS|CH|CL|CM|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[0-9A-Z]{1}[0-9]{1}$/,
        // RFC: 3-4 letras, 6 números, 3 homoclave
        rfc: /^([A-ZÑ&]{3,4}) ?(?:- ?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])) ?(?:- ?)?([A-Z\d]{2})([A\d])$/,
        // Solo números (para validar que no haya letras en campos numéricos)
        onlyNumbers: /^\d+$/,
        // Solo letras (para nombres)
        noNumbers: /^[a-zA-Z\sñÑáéíóúÁÉÍÓÚ]+$/
    };

    // --- Funciones de Utilidad ---

    // Muestra error en un campo específico
    function setError(input, message, feedbackId) {
        const feedback = document.getElementById(feedbackId);
        if (input) {
            input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
            input.classList.remove('border-green-500');
        }
        if (feedback) {
            feedback.textContent = message;
            feedback.className = "text-xs text-red-500 mt-1 font-medium block h-auto";
        }
        return false; // Retorna falso para indicar error
    }

    // Marca un campo como válido
    function setSuccess(input, feedbackId) {
        const feedback = document.getElementById(feedbackId);
        if (input) {
            input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
            input.classList.add('border-green-500');
        }
        if (feedback) {
            feedback.textContent = "";
        }
        return true;
    }

    // Validador de Fuerza de Contraseña
    function checkStrength(password, barId, feedbackId) {
        const bar = document.getElementById(barId);
        const feedback = document.getElementById(feedbackId);
        if (!bar) return false;

        let score = 0;
        if (password.length > 6) score++;
        if (password.length >= 8) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        // Resetear clases base
        bar.className = 'h-full transition-all duration-300 rounded-full';
        
        if (password.length === 0) {
            bar.style.width = '0%';
            if(feedback) feedback.textContent = '';
            return false;
        }

        let isValid = false;
        if (score <= 2) {
            bar.style.width = '30%';
            bar.classList.add('bg-red-500');
            if(feedback) { feedback.textContent = 'Débil'; feedback.className = 'text-xs mt-1 text-red-500 font-bold block'; }
        } else if (score <= 4) {
            bar.style.width = '70%';
            bar.classList.add('bg-yellow-400');
            if(feedback) { feedback.textContent = 'Media'; feedback.className = 'text-xs mt-1 text-yellow-600 font-bold block'; }
            isValid = true; // Aceptamos media como válida
        } else {
            bar.style.width = '100%';
            bar.classList.add('bg-green-500');
            if(feedback) { feedback.textContent = 'Fuerte'; feedback.className = 'text-xs mt-1 text-green-600 font-bold block'; }
            isValid = true;
        }
        return isValid;
    }

    // --- Validadores del Formulario Persona ---
    function validatePersonForm() {
        let isValid = true;

        const name = document.getElementById('id_person_first_name');
        const email = document.getElementById('id_person_email');
        const curp = document.getElementById('id_person_curp');
        const pass = document.getElementById('id_person_password');
        const confirm = document.getElementById('id_confirm_person_password');

        // Validar Nombre
        if (!name.value.trim()) isValid = setError(name, "El nombre es obligatorio", "person-name-feedback") && isValid;
        else if (!REGEX.noNumbers.test(name.value)) isValid = setError(name, "No debe contener números", "person-name-feedback") && isValid;
        else setSuccess(name, "person-name-feedback");

        // Validar Email
        if (!REGEX.email.test(email.value)) isValid = setError(email, "Correo inválido", "person-email-feedback") && isValid;
        else setSuccess(email, "person-email-feedback");

        // Validar CURP
        if (!REGEX.curp.test(curp.value.toUpperCase())) isValid = setError(curp, "CURP inválida (verifique formato)", "curp-feedback") && isValid;
        else setSuccess(curp, "curp-feedback");

        // Validar Contraseña (Fuerza)
        const isStrong = checkStrength(pass.value, "person-strength-bar", "person-password-feedback");
        if (!isStrong) {
            setError(pass, "La contraseña es muy débil (Min 8 caracteres, Mayúscula y Número)", "person-password-feedback");
            isValid = false;
        } 

        // Validar Confirmación
        if (pass.value !== confirm.value) isValid = setError(confirm, "Las contraseñas no coinciden", "person-confirm-feedback") && isValid;
        else if (!confirm.value) isValid = setError(confirm, "Confirma tu contraseña", "person-confirm-feedback") && isValid;
        else setSuccess(confirm, "person-confirm-feedback");

        return isValid;
    }

    // --- Validadores del Formulario Institución ---
    function validateInstitutionForm() {
        let isValid = true;

        const name = document.getElementById('id_institution_name');
        const rfc = document.getElementById('id_institution_rfc');
        const email = document.getElementById('id_institution_email');
        const pass = document.getElementById('id_institution_password');
        const confirm = document.getElementById('id_confirm_institution_password');

        if (!name.value.trim()) isValid = setError(name, "Nombre requerido", "inst-name-feedback") && isValid;
        else setSuccess(name, "inst-name-feedback");

        if (!REGEX.rfc.test(rfc.value.toUpperCase())) isValid = setError(rfc, "RFC inválido", "rfc-feedback") && isValid;
        else setSuccess(rfc, "rfc-feedback");

        if (!REGEX.email.test(email.value)) isValid = setError(email, "Correo inválido", "inst-email-feedback") && isValid;
        else setSuccess(email, "inst-email-feedback");

        const isStrong = checkStrength(pass.value, "inst-strength-bar", "inst-password-feedback");
        if (!isStrong) {
            setError(pass, "Contraseña débil", "inst-password-feedback");
            isValid = false;
        }

        if (pass.value !== confirm.value) isValid = setError(confirm, "No coinciden", "inst-confirm-feedback") && isValid;
        else if(!confirm.value) isValid = setError(confirm, "Requerido", "inst-confirm-feedback") && isValid;
        else setSuccess(confirm, "inst-confirm-feedback");

        return isValid;
    }

    // --- EVENT LISTENERS (Conexión con el HTML) ---

    // 1. Configurar Formulario Persona
    const formPerson = document.getElementById('form-person');
    if (formPerson) {
        // Bloquear envío si falla validación
        formPerson.addEventListener('submit', (e) => {
            if (!validatePersonForm()) {
                e.preventDefault(); // ¡IMPORTANTE! Esto detiene el envío
                console.log("Formulario Persona inválido");
            }
        });

        // Feedback en tiempo real para contraseña
        const pPass = document.getElementById('id_person_password');
        const pConf = document.getElementById('id_confirm_person_password');
        
        if (pPass) {
            pPass.addEventListener('input', () => {
                checkStrength(pPass.value, "person-strength-bar", "person-password-feedback");
                // Si ya escribió confirmación, validar coincidencia al vuelo
                if(pConf.value) { 
                    if(pPass.value !== pConf.value) setError(pConf, "Las contraseñas no coinciden", "person-confirm-feedback");
                    else setSuccess(pConf, "person-confirm-feedback");
                }
            });
        }

        if (pConf) {
            pConf.addEventListener('input', () => {
                if(pPass.value !== pConf.value) setError(pConf, "Las contraseñas no coinciden", "person-confirm-feedback");
                else setSuccess(pConf, "person-confirm-feedback");
            });
        }
    }

    // 2. Configurar Formulario Institución
    const formInst = document.getElementById('form-institution');
    if (formInst) {
        formInst.addEventListener('submit', (e) => {
            if (!validateInstitutionForm()) {
                e.preventDefault();
                console.log("Formulario Institución inválido");
            }
        });

        const iPass = document.getElementById('id_institution_password');
        const iConf = document.getElementById('id_confirm_institution_password');

        if (iPass) {
            iPass.addEventListener('input', () => {
                checkStrength(iPass.value, "inst-strength-bar", "inst-password-feedback");
                if(iConf.value) {
                    if(iPass.value !== iConf.value) setError(iConf, "No coinciden", "inst-confirm-feedback");
                    else setSuccess(iConf, "inst-confirm-feedback");
                }
            });
        }

        if (iConf) {
            iConf.addEventListener('input', () => {
                if(iPass.value !== iConf.value) setError(iConf, "No coinciden", "inst-confirm-feedback");
                else setSuccess(iConf, "inst-confirm-feedback");
            });
        }
    }
});