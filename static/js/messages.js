
// Mensagens do Sweet Alert 2

document.addEventListener('click', async function (event) {
    const botao = event.target.closest('.js-inativar');

    if (!botao) {
        return;
    }

    const formulario = botao.closest('.js-form-inativar');
    const nome = formulario.dataset.nome;

    const resultado = await Swal.fire({
        title: 'Excluir cadastro?',
        text: `Deseja realmente excluir o cadastro de ${nome}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, excluir',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#263563',
        reverseButtons: true,
        focusCancel: true
    });

    if (resultado.isConfirmed) {
        formulario.requestSubmit();
    }
});