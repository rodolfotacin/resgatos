
// Visualizar senha e loading do botão Entrar
document.addEventListener('DOMContentLoaded', function () {

    // Visualizar senha
    const passwordInput = document.getElementById('password');
    const toggleButton = document.getElementById('toggle-password');

    if (passwordInput && toggleButton) {
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
    }

    // Loading do botão Entrar
    const form = document.querySelector('form');
    const btnEntrar = document.getElementById('btnEntrar');
    const textoEntrar = document.getElementById('textoEntrar');
    const loadingEntrar = document.getElementById('loadingEntrar');

    if (form && btnEntrar && textoEntrar && loadingEntrar) {
        form.addEventListener('submit', function (event) {

            // Evita envios repetidos
            if (form.dataset.enviando === 'true') {
                event.preventDefault();
                return;
            }

            form.dataset.enviando = 'true';

            textoEntrar.classList.add('d-none');
            loadingEntrar.classList.remove('d-none');

            btnEntrar.disabled = true;
        });
    }

});
