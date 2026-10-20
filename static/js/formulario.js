 // Máscaras e funcionalidades do formulário

$(document).ready(function () {

    // CPF
    $('.js-cpf').mask('000.000.000-00');

    // CEP
    $('.js-cep').mask('00000-000');

    // Consulta de CEP - ViaCEP
    const campoCep = document.querySelector('.js-cep');

    if (campoCep) {
        // Área para mensagens ao usuário
        const feedbackCep = document.createElement('div');
        feedbackCep.className = 'form-text mt-1';
        feedbackCep.setAttribute('aria-live', 'polite');
        campoCep.insertAdjacentElement('afterend', feedbackCep);

        campoCep.addEventListener('blur', async function () {
            const cep = this.value.replace(/\D/g, '');

            // Consulta somente quando houver 8 dígitos
            if (cep.length !== 8) {
                feedbackCep.textContent = '';
                return;
            }

            feedbackCep.textContent = 'Consultando CEP...';

            try {
                const resposta = await fetch(
                    `https://viacep.com.br/ws/${cep}/json/`
                );

                if (!resposta.ok) {
                    throw new Error('Falha na consulta');
                }

                const dados = await resposta.json();

                if (dados.erro) {
                    feedbackCep.textContent = 'CEP não encontrado.';
                    return;
                }

                const camposEndereco = {
                    endereco: dados.logradouro,
                    bairro: dados.bairro,
                    cidade: dados.localidade,
                    estado: dados.uf
                };

                Object.entries(camposEndereco).forEach(([nome, valor]) => {
                    const campo = document.querySelector(
                        `[name="${nome}"]`
                    );

                    if (campo) {
                        campo.value = valor || '';
                    }
                });

                feedbackCep.textContent =
                    'Endereço preenchido. Confira os dados antes de salvar.';

            } catch (erro) {
                feedbackCep.textContent =
                    'Não foi possível consultar o CEP. Tente novamente.';
                console.error('Erro ao consultar ViaCEP:', erro);
            }
        });
    }

    // Telefone - intl-tel-input
    const inputTelefone = document.querySelector('.js-telefone');

    if (inputTelefone && window.intlTelInput) {
        const iti = window.intlTelInput(inputTelefone, {
            initialCountry: 'br',
            preferredCountries: ['br', 'pt', 'us'],
            separateDialCode: true,
            countryNameLocale: 'pt',
            loadUtils: () => import(
                '/static/vendor/intl-tel-input/js/utils.js'
            )
        });

        const formularioTelefone = inputTelefone.form;

        if (formularioTelefone) {
            formularioTelefone.addEventListener('submit', async function () {
                try {
                    if (iti.promise) {
                        await iti.promise;
                    }

                    if (iti.isValidNumber()) {
                        inputTelefone.value = iti.getNumber();
                    }
                } catch (erro) {
                    console.error(
                        'Erro ao preparar o telefone:',
                        erro
                    );
                }
            });
        }
    }


    // Acesso ao sistema
    const formularioAcesso = document.querySelector('form[data-modo]');
    const checkboxAcesso = document.querySelector('#possui_acesso');
    const camposAcesso = document.querySelector('#campos-acesso');

    if (formularioAcesso && checkboxAcesso && camposAcesso) {
        const campos = camposAcesso.querySelectorAll('input');

        function atualizarCamposAcesso() {
            const possuiAcesso = checkboxAcesso.checked;

            camposAcesso.hidden = !possuiAcesso;

            campos.forEach(campo => {
                campo.disabled = !possuiAcesso;
            });
        }

        checkboxAcesso.addEventListener('change', function () {
            if (checkboxAcesso.checked) {
                // Ao conceder acesso, seleciona Habilitado.
                const radioHabilitado = camposAcesso.querySelector(
                    'input[name="usuario_is_active"][value="true"]'
                );

                if (radioHabilitado) {
                    radioHabilitado.checked = true;
                }
            }

            atualizarCamposAcesso();
        });

        atualizarCamposAcesso();
    }


    // Consulta de CPF ao sair do campo
    const campoCpf = document.querySelector('#cpf');

    if (campoCpf) {
        let ultimaConsulta = '';

        campoCpf.addEventListener('blur', async function () {
            const cpf = this.value.trim();
            const numeros = cpf.replace(/\D/g, '');

            if (numeros.length !== 11 || numeros === ultimaConsulta) {
                return;
            }

            ultimaConsulta = numeros;

            try {
                const url = new URL(
                    campoCpf.dataset.url,
                    window.location.origin
                );

                url.searchParams.set('cpf', numeros);

                const resposta = await fetch(url);

                if (!resposta.ok) {
                    throw new Error('Falha na consulta do CPF.');
                }

                const resultado = await resposta.json();

                if (!resultado.encontrado) {
                    return;
                }

                // Não direciona para a própria tela de edição.
                const formulario = campoCpf.closest('form');
                const modo = formulario?.dataset.modo;

                if (modo === 'editar') {
                    return;
                }

                if (resultado.is_active) {
                    const confirmacao = await Swal.fire({
                        title: 'Cadastro localizado',
                        text: `${resultado.nome} já possui cadastro. Deseja abrir a edição?`,
                        icon: 'info',
                        showCancelButton: true,
                        confirmButtonText: 'Abrir cadastro',
                        cancelButtonText: 'Cancelar',
                        confirmButtonColor: '#263563'
                    });

                    if (confirmacao.isConfirmed) {
                        window.location.href = resultado.url_editar;
                    }

                    return;
                }

                const confirmacao = await Swal.fire({
                    title: 'Cadastro localizado',
                    text: `O cadastro de ${resultado.nome} está inativo. Deseja reativá-lo?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sim, reativar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#263563'
                });

                if (confirmacao.isConfirmed) {
                    window.location.href =
                        resultado.url_editar + '?reativar=1';
                } else {
                    window.location.href = '/pessoas/lista/';
                }

            } catch (erro) {
                console.error('Erro ao consultar CPF:', erro);

                Swal.fire({
                    title: 'Não foi possível consultar',
                    text: 'Ocorreu um erro ao verificar o CPF. Tente novamente.',
                    icon: 'error',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#263563'
                });
            }
        });
    }

});
