 // Máscaras e funcionalidades do formulário

$(document).ready(function () {

    // CPF
    $('.js-cpf').mask('000.000.000-00');

    // CEP
    $('.js-cep').mask('00000-000');

    // CNPJ
    $('.js-cnpj').mask('00.000.000/0000-00');

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


    // Fancybox - Visualização ampliada de fotos
    if (window.Fancybox) {

        Fancybox.bind('[data-fancybox="pet-photo"]', {
            Carousel: {
                Thumbs: false,
                Toolbar: {
                    display: {
                        left: [],
                        middle: [],
                        right: ['close'],
                    },
                },
                Zoomable: {
                    Panzoom: {
                        maxScale: 'cover',
                        panMode: 'mousemove',
                        mouseMoveFactor: 1.1,
                    },
                },
            },
        });

        Fancybox.bind('[data-fancybox="pessoa-photo"]', {
            Carousel: {
                Thumbs: false,
                Toolbar: {
                    display: {
                        left: [],
                        middle: [],
                        right: ['close'],
                    },
                },
                Zoomable: {
                    Panzoom: {
                        maxScale: 'cover',
                        panMode: 'mousemove',
                        mouseMoveFactor: 1.1,
                    },
                },
            },
        });

    }


    // Confirmação da remoção da foto do cadastro
    $('#btn-remover-foto').on('click', function (event) {
        event.preventDefault();

        const botao = this;
        const formulario = botao.form;

        Swal.fire({
            title: 'Remover foto?',
            text: 'A foto será removida permanentemente.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sim, remover',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#d63939',
            reverseButtons: true,
        }).then((resultado) => {
            if (resultado.isConfirmed) {
                // Cria um campo oculto para identificar a operação.
                let campo = formulario.querySelector(
                    'input[name="remover_foto"]'
                );

                if (!campo) {
                    campo = document.createElement('input');
                    campo.type = 'hidden';
                    campo.name = 'remover_foto';
                    campo.value = '1';
                    formulario.appendChild(campo);
                }

                formulario.requestSubmit();
            }
        });
    });


    // Consulta de CNPJ ao sair do campo
    const campoCnpj = document.querySelector('#cnpj');
    const statusCnpj = document.querySelector('#cnpj-status');

    if (campoCnpj) {
        let ultimaConsulta = '';
        let consultando = false;

        function somenteNumeros(valor) {
            return valor.replace(/\D/g, '');
        }

        async function consultarFornecedor() {
            const cnpj = somenteNumeros(campoCnpj.value);

            if (
                cnpj.length !== 14 ||
                cnpj === cnpj[0].repeat(14) ||
                cnpj === ultimaConsulta ||
                consultando
            ) {
                return;
            }

            consultando = true;

            if (statusCnpj) {
                statusCnpj.textContent = 'Consultando CNPJ...';
            }

            try {
                const url = new URL(
                    campoCnpj.dataset.url,
                    window.location.origin
                );

                url.searchParams.set('cnpj', cnpj);

                const resposta = await fetch(url);

                if (!resposta.ok) {
                    throw new Error('Falha na consulta do CNPJ.');
                }

                const resultado = await resposta.json();

                if (somenteNumeros(campoCnpj.value) !== cnpj) {
                    return;
                }

                ultimaConsulta = cnpj;

                if (statusCnpj) {
                    statusCnpj.textContent = '';
                }

                if (!resultado.encontrado) {
                    return;
                }

                const confirmacao = await Swal.fire({
                    title: resultado.is_active
                        ? 'Fornecedor encontrado'
                        : 'Fornecedor inativo',
                    text: resultado.is_active
                        ? `O cadastro de ${resultado.nome} já existe. Deseja editá-lo?`
                        : `O cadastro de ${resultado.nome} está inativo. Deseja reativá-lo e editá-lo?`,
                    icon: resultado.is_active ? 'info' : 'warning',
                    showCancelButton: true,
                    confirmButtonText: resultado.is_active
                        ? 'Abrir cadastro'
                        : 'Reativar e editar',
                    cancelButtonText: 'Continuar',
                    confirmButtonColor: '#263563'
                });

                if (confirmacao.isConfirmed) {
                    const destino = new URL(
                        resultado.url_editar,
                        window.location.origin
                    );

                    if (!resultado.is_active) {
                        destino.searchParams.set('reativar', '1');
                    }

                    window.location.href = destino.href;
                }

            } catch (erro) {
                console.error('Erro ao consultar CNPJ:', erro);

                if (statusCnpj) {
                    statusCnpj.textContent =
                        'Não foi possível consultar o CNPJ. Tente novamente.';
                }

                ultimaConsulta = '';

            } finally {
                consultando = false;
            }
        }

        campoCnpj.addEventListener('blur', consultarFornecedor);

        campoCnpj.addEventListener('input', function () {
            const cnpj = somenteNumeros(this.value);

            if (cnpj !== ultimaConsulta) {
                ultimaConsulta = '';
            }
        });
    }


});
