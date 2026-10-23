
document.addEventListener('DOMContentLoaded', function () {
    const chave = 'resgatos-tamanho-fonte';
    const padrao = 100;
    const minimo = 100;
    const maximo = 200;
    const passo = 10;

    const botoes = {
        aumentar: document.getElementById('aumentar-fonte'),
        diminuir: document.getElementById('diminuir-fonte'),
        restaurar: document.getElementById('restaurar-fonte')
    };

    if (!botoes.aumentar || !botoes.diminuir || !botoes.restaurar) {
        console.error('Acessibilidade: não foi possível localizar todos os botões.');
        return;
    }

    let tamanho = padrao;

    try {
        const salvo = Number(localStorage.getItem(chave));
        if (salvo >= minimo && salvo <= maximo) {
            tamanho = salvo;
        }
    } catch (erro) {
        console.warn('Acessibilidade: não foi possível ler a preferência salva.');
    }

    function aplicar(valor) {
        tamanho = Math.max(minimo, Math.min(maximo, valor));

        // A escala afeta unidades rem usadas pelo Tabler.
        document.documentElement.style.fontSize =
            (16 * tamanho / 100) + 'px';

        try {
            localStorage.setItem(chave, String(tamanho));
        } catch (erro) {
            console.warn('Acessibilidade: não foi possível salvar a preferência.');
        }

        console.info('Acessibilidade: fonte em ' + tamanho + '%');
    }

    botoes.aumentar.addEventListener('click', function () {
        aplicar(tamanho + passo);
    });

    botoes.diminuir.addEventListener('click', function () {
        aplicar(tamanho - passo);
    });

    botoes.restaurar.addEventListener('click', function () {
        aplicar(padrao);
    });

    aplicar(tamanho);
    console.info('Acessibilidade: controles inicializados.');
});
