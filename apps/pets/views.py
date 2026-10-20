from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import render

from .models import Pet, PessoaPet


@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    vinculos_ativos = PessoaPet.objects.filter(
        data_fim__isnull=True
    ).select_related('pessoa')

    pets = Pet.objects.prefetch_related(
        Prefetch(
            'vinculos_pessoas',
            queryset=vinculos_ativos,
            to_attr='vinculos_atuais',
        )
    )

    if busca:
        pets = pets.filter(
            Q(nome__icontains=busca)
            | Q(microchip__icontains=busca)
            | Q(vinculos_pessoas__pessoa__nome__icontains=busca)
        ).distinct()

    pets = pets.order_by('nome')

    paginator = Paginator(pets, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'pets/lista.html',
        {
            'pets': page_obj.object_list,
            'busca': busca,
            'por_pagina': por_pagina,
            'page_obj': page_obj,
            'paginator': paginator,
        }
    )