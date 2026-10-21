from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from apps.resgates.models import Resgate

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


@login_required
def adicionar(request):
    dados = {
        'nome': '',
        'microchip': '',
        'especie': '',
        'raca': '',
        'sexo': '',
        'cor': '',
        'data_nascimento': '',
        'porte': '',
        'pelagem': '',
        'observacoes': '',
        'is_active': True,
    }

    if request.method == 'POST':
        dados = {
            'nome': request.POST.get('nome', '').strip(),
            'microchip': request.POST.get('microchip', '').strip() or None,
            'especie': request.POST.get('especie', '').strip(),
            'raca': request.POST.get('raca', '').strip() or None,
            'sexo': request.POST.get('sexo', '').strip() or None,
            'cor': request.POST.get('cor', '').strip() or None,
            'data_nascimento': request.POST.get('data_nascimento', '').strip() or None,
            'porte': request.POST.get('porte', '').strip() or None,
            'pelagem': request.POST.get('pelagem', '').strip() or None,
            'observacoes': request.POST.get('observacoes', '').strip() or None,
            'is_active': request.POST.get('is_active', 'true') == 'true',
        }

        obrigatorios = ['nome', 'especie']

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha os campos obrigatórios.'
            )
            return render(
                request,
                'pets/formulario.html',
                {'dados': dados},
            )

        try:
            data_nascimento = (
                date.fromisoformat(dados['data_nascimento'])
                if dados['data_nascimento']
                else None
            )
        except ValueError:
            messages.error(
                request,
                'Informe uma data de nascimento válida.'
            )
            return render(
                request,
                'pets/formulario.html',
                {'dados': dados},
            )

        foto = request.FILES.get('foto')

        Pet.objects.create(
            nome=dados['nome'],
            microchip=dados['microchip'],
            especie=dados['especie'],
            raca=dados['raca'],
            sexo=dados['sexo'],
            cor=dados['cor'],
            data_nascimento=data_nascimento,
            porte=dados['porte'],
            pelagem=dados['pelagem'],
            foto=foto,
            observacoes=dados['observacoes'],
            is_active=dados['is_active'],
        )

        messages.success(
            request,
            'Pet cadastrado com sucesso.'
        )
        return redirect('pets:lista')

    return render(
        request,
        'pets/formulario.html',
        {'dados': dados},
    )



@login_required
def editar(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)

    aba = request.POST.get(
        'aba',
        request.GET.get('aba', '')
    )

    dados = {
        'nome': pet.nome,
        'microchip': pet.microchip or '',
        'especie': pet.especie,
        'raca': pet.raca or '',
        'sexo': pet.sexo or '',
        'cor': pet.cor or '',
        'data_nascimento': pet.data_nascimento or '',
        'porte': pet.porte or '',
        'pelagem': pet.pelagem or '',
        'observacoes': pet.observacoes or '',
        'is_active': pet.is_active,
    }

    resgates = Resgate.objects.filter(
        pet=pet,
        is_active=True
    ).order_by('-data_resgate', '-id')

    if request.method == 'POST':
        dados = {
            'nome': request.POST.get('nome', '').strip(),
            'microchip': request.POST.get('microchip', '').strip() or None,
            'especie': request.POST.get('especie', '').strip(),
            'raca': request.POST.get('raca', '').strip() or None,
            'sexo': request.POST.get('sexo', '').strip() or None,
            'cor': request.POST.get('cor', '').strip() or None,
            'data_nascimento': request.POST.get(
                'data_nascimento', ''
            ).strip() or None,
            'porte': request.POST.get('porte', '').strip() or None,
            'pelagem': request.POST.get('pelagem', '').strip() or None,
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip() or None,
            'is_active': request.POST.get('is_active') == 'true',
        }

        if not dados['nome'] or not dados['especie']:
            messages.error(
                request,
                'Preencha os campos obrigatórios.'
            )
            return render(
                request,
                'pets/formulario.html',
                {
                    'pet': pet,
                    'dados': dados,
                    'resgates': resgates,
                },
            )

        try:
            data_nascimento = (
                date.fromisoformat(dados['data_nascimento'])
                if dados['data_nascimento']
                else None
            )
        except ValueError:
            messages.error(
                request,
                'Informe uma data de nascimento válida.'
            )
            return render(
                request,
                'pets/formulario.html',
                {
                    'pet': pet,
                    'dados': dados,
                    'resgates': resgates,
                },
            )

        with transaction.atomic():
            pet.nome = dados['nome']
            pet.microchip = dados['microchip']
            pet.especie = dados['especie']
            pet.raca = dados['raca']
            pet.sexo = dados['sexo']
            pet.cor = dados['cor']
            pet.data_nascimento = data_nascimento
            pet.porte = dados['porte']
            pet.pelagem = dados['pelagem']
            pet.observacoes = dados['observacoes']
            pet.is_active = dados['is_active']

            foto = request.FILES.get('foto')
            remover_foto = request.POST.get('remover_foto') == '1'

            foto_anterior = None

            if remover_foto and pet.foto:
                foto_anterior = pet.foto
                pet.foto = None

            elif foto:
                pet.foto = foto

            pet.save()

            if foto_anterior:
                foto_anterior.delete(save=False)

        messages.success(
            request,
            'Pet atualizado com sucesso.'
        )

        url = reverse('pets:editar', args=[pet.id])

        if aba:
            url = f'{url}?aba={aba}'

        return redirect(url)

    return render(
        request,
        'pets/formulario.html',
        {
            'pet': pet,
            'dados': dados,
            'resgates': resgates,
        },
    )
