from datetime import date
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.db import transaction
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from apps.resgates.models import Resgate

from .models import Pet, PessoaPet, PetSituacao


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

    situacoes = PetSituacao.objects.filter(
        pet=pet
    ).annotate(
        prioridade=Case(
            When(data_fim__isnull=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('prioridade', '-data_inicio', '-id')

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
                    'situacoes': situacoes,
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
                    'situacoes': situacoes,
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
            'situacoes': situacoes,
        },
    )


@login_required
def situacao_adicionar(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)

    dados = {
        'situacao': '',
        'data_inicio': timezone.localdate().isoformat(),
        'data_fim': '',
        'observacoes': '',
    }

    erros = []

    if request.method == 'POST':
        dados = {
            'situacao': request.POST.get('situacao', '').strip(),
            'data_inicio': request.POST.get('data_inicio', '').strip(),
            'data_fim': request.POST.get('data_fim', '').strip(),
            'observacoes': request.POST.get('observacoes', '').strip(),
        }

        situacao = dados['situacao']
        data_inicio_str = dados['data_inicio']
        data_fim_str = dados['data_fim']
        observacoes = dados['observacoes'] or None

        if not situacao:
            erros.append('Informe a situação do pet.')

        try:
            data_inicio = date.fromisoformat(data_inicio_str)
        except ValueError:
            data_inicio = None
            erros.append('Informe uma data de início válida.')

        try:
            data_fim = (
                date.fromisoformat(data_fim_str)
                if data_fim_str else None
            )
        except ValueError:
            data_fim = None
            erros.append('Informe uma data final válida.')

        if data_inicio and data_fim and data_fim < data_inicio:
            erros.append(
                'A data final não pode ser anterior à data de início.'
            )

        if not erros:
            PetSituacao.objects.create(
                pet=pet,
                situacao=situacao,
                data_inicio=data_inicio,
                data_fim=data_fim,
                observacoes=observacoes,
            )

            messages.success(
                request,
                'Situação registrada com sucesso.'
            )

            return redirect(
                f"{reverse('pets:editar', args=[pet.id])}?aba=situacoes"
            )

    return render(
        request,
        'pets/situacoes/formulario.html',
        {
            'pet': pet,
            'dados': dados,
            'erros': erros,
        }
    )


@login_required
def situacao_editar(request, pet_id, situacao_id):
    pet = get_object_or_404(Pet, pk=pet_id)

    situacao_pet = get_object_or_404(
        PetSituacao,
        pk=situacao_id,
        pet=pet,
    )

    if request.method == 'POST':
        descricao = request.POST.get('situacao', '').strip()
        data_inicio_str = request.POST.get('data_inicio', '').strip()
        data_fim_str = request.POST.get('data_fim', '').strip()
        observacoes = request.POST.get('observacoes', '').strip() or None

        erros = []

        if not descricao:
            erros.append('Informe a situação do pet.')

        try:
            data_inicio = date.fromisoformat(data_inicio_str)
        except ValueError:
            data_inicio = None
            erros.append('Informe uma data de início válida.')

        try:
            data_fim = date.fromisoformat(data_fim_str) if data_fim_str else None
        except ValueError:
            data_fim = None
            erros.append('Informe uma data final válida.')

        if data_inicio and data_fim and data_fim < data_inicio:
            erros.append('A data final não pode ser anterior à data de início.')

        if erros:
            dados = {
                'situacao': descricao,
                'data_inicio': data_inicio_str,
                'data_fim': data_fim_str,
                'observacoes': observacoes or '',
            }

            return render(
                request,
                'pets/situacoes/formulario.html',
                {
                    'pet': pet,
                    'situacao_obj': situacao_pet,
                    'dados': dados,
                    'erros': erros,
                },
            )

        situacao_pet.situacao = descricao
        situacao_pet.data_inicio = data_inicio
        situacao_pet.data_fim = data_fim
        situacao_pet.observacoes = observacoes
        situacao_pet.save()

        messages.success(request, 'Situação atualizada com sucesso.')

        return redirect(
            f"{reverse('pets:editar', args=[pet.id])}?aba=situacoes"
        )

    dados = {
        'situacao': situacao_pet.situacao,
        'data_inicio': situacao_pet.data_inicio.isoformat(),
        'data_fim': (
            situacao_pet.data_fim.isoformat()
            if situacao_pet.data_fim
            else ''
        ),
        'observacoes': situacao_pet.observacoes or '',
    }

    return render(
        request,
        'pets/situacoes/formulario.html',
        {
            'pet': pet,
            'situacao_obj': situacao_pet,
            'dados': dados,
            'erros': [],
        },
    )


@login_required
def situacao_excluir(request, pet_id, situacao_id):
    if request.method != 'POST':
        return redirect(
            f"{reverse('pets:editar', args=[pet_id])}?aba=situacoes"
        )

    pet = get_object_or_404(Pet, pk=pet_id)

    situacao_pet = get_object_or_404(
        PetSituacao,
        pk=situacao_id,
        pet=pet,
    )

    situacao_pet.delete()

    messages.success(request, 'Situação excluída com sucesso.')

    return redirect(
        f"{reverse('pets:editar', args=[pet.id])}?aba=situacoes"
    )