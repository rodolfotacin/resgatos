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

                // Preenche os campos do endereço
                const campos = {
                    endereco: dados.logradouro,
                    bairro: dados.bairro,
                    cidade: dados.localidade,
                    estado: dados.uf
                };

                Object.entries(campos).forEach(([nome, valor]) => {
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
    const inputElement = document.querySelector(".js-telefone");
    if (!inputElement) return;

    const iti = window.intlTelInput(inputElement, {
        initialCountry: "br",
        preferredCountries:[
            "br",
            "pt",
            "us"
        ],
        separateDialCode: true,
        countryNameLocale: "pt",
        loadUtils: () => import('/static/vendor/intl-tel-input/js/utils.js')
    });


    // Formata dados do telefone para persistencia
    const formulario = inputElement.form;

    if (formulario) {
        formulario.addEventListener('submit', async function () {
            try {
                if (iti.promise) {
                    await iti.promise;
                }

                if (iti.isValidNumber()) {
                    inputElement.value = iti.getNumber();
                }
            } catch (erro) {
                console.error('Erro ao preparar o telefone:', erro);
            }
        });
    }


    // Acesso ao sistema
    const checkboxAcesso = document.querySelector('#possui_acesso');
    const camposAcesso = document.querySelector('#campos-acesso');

    if (checkboxAcesso && camposAcesso) {
        const campos = camposAcesso.querySelectorAll('input');

        const radiosStatus = camposAcesso.querySelectorAll(
            'input[name="usuario_is_active"]'
        );

        function atualizarCamposAcesso() {
            const possuiAcesso = checkboxAcesso.checked;

            // Exibe ou oculta os campos
            camposAcesso.hidden = !possuiAcesso;

            // Habilita ou desabilita os campos
            campos.forEach(function (campo) {
                campo.disabled = !possuiAcesso;
            });

            // Sincroniza o status do acesso
            radiosStatus.forEach(function (radio) {
                radio.checked = radio.value === String(possuiAcesso);
            });
        }

        checkboxAcesso.addEventListener(
            'change',
            atualizarCamposAcesso
        );

        atualizarCamposAcesso();
    }


});
