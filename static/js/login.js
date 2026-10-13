
    // Visualizar senha

    document.addEventListener('DOMContentLoaded', function () {
        const passwordInput = document.getElementById('password');
        const toggleButton = document.getElementById('toggle-password');

        if (!passwordInput || !toggleButton) {
            return;
        }

        toggleButton.addEventListener('click', function () {
            const mostrarSenha = passwordInput.type === 'password';

            passwordInput.type = mostrarSenha ? 'text' : 'password';

            toggleButton.setAttribute('aria-pressed', String(mostrarSenha));
            toggleButton.setAttribute(
                'aria-label',
                mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'
            );

            const icon = toggleButton.querySelector('i');

            if (icon) {
                icon.classList.toggle('ti-eye', !mostrarSenha);
                icon.classList.toggle('ti-eye-off', mostrarSenha);
            }
        });
    });
