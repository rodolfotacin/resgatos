from datetime import date
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from apps.resgates.models import Resgate
from apps.pessoas.models import Pessoa

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

    pets = Pet.objects.filter(
        is_active=True
    ).prefetch_related(
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
            is_active=True,
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

    if not pet.is_active:
        pet.is_active = True
        pet.save(update_fields=['is_active'])

    pessoas_relacionadas = PessoaPet.objects.filter(
        pet=pet
    ).select_related(
        'pessoa'
    ).order_by(
        'pessoa__nome'
    )

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
                    'pessoas_relacionadas': pessoas_relacionadas,
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
                    'pessoas_relacionadas': pessoas_relacionadas,
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
            'pessoas_relacionadas': pessoas_relacionadas,
        },
    )


@login_required
def inativar(request, pet_id):
    if request.method != 'POST':
        return redirect('pets:lista')

    pet = get_object_or_404(
        Pet,
        pk=pet_id,
        is_active=True,
    )

    with transaction.atomic():
        pet.is_active = False
        pet.save(update_fields=['is_active', 'updated_at'])

    messages.success(
        request,
        'Pet excluído com sucesso.'
    )

    return redirect('pets:lista')


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



@login_required
def associar_pessoa(request, pessoa_id):
    pessoa = get_object_or_404(Pessoa, pk=pessoa_id)

    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    pets = Pet.objects.filter(is_active=True)

    if busca:
        pets = pets.filter(
            Q(nome__icontains=busca) |
            Q(microchip__icontains=busca)
        )

    pets = pets.order_by('nome')

    paginator = Paginator(pets, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page'))

    dados = {
        'tipo_relacao': '',
        'data_inicio': timezone.localdate().isoformat(),
        'data_fim': '',
        'observacoes': '',
    }

    pet_selecionado = None
    erros = []

    if request.method == 'POST':
        dados = {
            'tipo_relacao': request.POST.get(
                'tipo_relacao', ''
            ).strip(),
            'data_inicio': request.POST.get(
                'data_inicio', ''
            ).strip(),
            'data_fim': request.POST.get(
                'data_fim', ''
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        pet_id = request.POST.get('pet_id', '').strip()

        try:
            pet_selecionado = Pet.objects.get(
                pk=pet_id,
                is_active=True,
            )
        except (Pet.DoesNotExist, ValueError):
            erros.append('Selecione um pet válido.')

        if not dados['tipo_relacao']:
            erros.append('Informe o tipo de relação.')

        try:
            data_inicio = date.fromisoformat(dados['data_inicio'])
        except ValueError:
            data_inicio = None
            erros.append('Informe uma data de início válida.')

        try:
            data_fim = (
                date.fromisoformat(dados['data_fim'])
                if dados['data_fim']
                else None
            )
        except ValueError:
            data_fim = None
            erros.append('Informe uma data de término válida.')

        if data_inicio and data_fim and data_fim < data_inicio:
            erros.append(
                'A data de término não pode ser anterior à data de início.'
            )

        if pet_selecionado and PessoaPet.objects.filter(
            pessoa=pessoa,
            pet=pet_selecionado,
            data_fim__isnull=True,
        ).exists():
            erros.append(
                'Este pet já possui um vínculo vigente com esta pessoa.'
            )

        if not erros:
            PessoaPet.objects.create(
                pessoa=pessoa,
                pet=pet_selecionado,
                tipo_relacao=dados['tipo_relacao'],
                data_inicio=data_inicio,
                data_fim=data_fim,
                observacoes=dados['observacoes'] or None,
            )

            messages.success(
                request,
                'Pet associado à pessoa com sucesso.',
            )

            return redirect(
                f"{reverse('pessoas:editar', args=[pessoa.id])}?aba=pets"
            )

    return render(
        request,
        'pets/associar_pessoa.html',
        {
            'pessoa': pessoa,
            'pets': page_obj.object_list,
            'busca': busca,
            'por_pagina': por_pagina,
            'page_obj': page_obj,
            'paginator': paginator,
            'dados': dados,
            'pet_selecionado': pet_selecionado,
            'erros': erros,
        },
    )


@login_required
def editar_associacao(request, vinculo_id):
    vinculo = get_object_or_404(
        PessoaPet.objects.select_related('pessoa', 'pet'),
        pk=vinculo_id,
    )

    pessoa = vinculo.pessoa
    pet = vinculo.pet

    origem = request.GET.get(
        'origem',
        request.POST.get('origem', 'pessoa')
    )

    if origem not in ('pessoa', 'pet'):
        origem = 'pessoa'

    dados = {
        'tipo_relacao': vinculo.tipo_relacao,
        'data_inicio': vinculo.data_inicio.isoformat(),
        'data_fim': (
            vinculo.data_fim.isoformat()
            if vinculo.data_fim else ''
        ),
        'observacoes': vinculo.observacoes or '',
    }

    erros = []

    if request.method == 'POST':
        dados = {
            'tipo_relacao': request.POST.get(
                'tipo_relacao', ''
            ).strip(),
            'data_inicio': request.POST.get(
                'data_inicio', ''
            ).strip(),
            'data_fim': request.POST.get(
                'data_fim', ''
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        if not dados['tipo_relacao']:
            erros.append('Informe o tipo de relação.')

        try:
            data_inicio = date.fromisoformat(
                dados['data_inicio']
            )
        except (ValueError, TypeError):
            data_inicio = None
            erros.append('Informe uma data de início válida.')

        if dados['data_fim']:
            try:
                data_fim = date.fromisoformat(
                    dados['data_fim']
                )
            except (ValueError, TypeError):
                data_fim = None
                erros.append('Informe uma data de término válida.')
        else:
            data_fim = None

        if (
            data_inicio
            and data_fim
            and data_fim < data_inicio
        ):
            erros.append(
                'A data de término não pode ser anterior '
                'à data de início.'
            )

        # Impede outro vínculo vigente para a mesma pessoa e pet.
        if (
            data_fim is None
            and PessoaPet.objects.filter(
                pessoa=vinculo.pessoa,
                pet=vinculo.pet,
                data_fim__isnull=True,
            ).exclude(pk=vinculo.pk).exists()
        ):
            erros.append(
                'Já existe um vínculo vigente entre esta '
                'pessoa e este pet.'
            )

        if not erros:
            vinculo.tipo_relacao = dados['tipo_relacao']
            vinculo.data_inicio = data_inicio
            vinculo.data_fim = data_fim
            vinculo.observacoes = dados['observacoes'] or None

            vinculo.save()

            messages.success(
                request,
                'Vínculo atualizado com sucesso.',
            )

            if origem == 'pet':
                return redirect(
                    f"{reverse('pets:editar', args=[pet.id])}"
                    "?aba=pessoas"
                )

            return redirect(
                f"{reverse('pessoas:editar', args=[pessoa.id])}"
                "?aba=pets"
            )

    return render(
        request,
        'pets/editar_associacao.html',
        {
            'vinculo': vinculo,
            'pessoa': pessoa,
            'pet': vinculo.pet,
            'dados': dados,
            'erros': erros,
        },
    )


@login_required
@require_POST
def excluir_vinculo_pet(request, pessoa_id=None, vinculo_id=None):
    origem = request.POST.get('origem', 'pessoa')

    vinculo = get_object_or_404(
        PessoaPet.objects.select_related('pessoa', 'pet'),
        pk=vinculo_id,
    )

    if pessoa_id is not None and vinculo.pessoa_id != pessoa_id:
        return redirect('pets:lista')

    pessoa = vinculo.pessoa
    pet = vinculo.pet

    vinculo.delete()

    messages.success(
        request,
        'Vínculo com o pet excluído com sucesso.',
    )

    if origem == 'pet':
        return redirect(
            f"{reverse('pets:editar', args=[pet.id])}?aba=pessoas"
        )

    return redirect(
        f"{reverse('pessoas:editar', args=[pessoa.id])}?aba=pets"
    )


@login_required
def associar_pet_pessoa(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)

    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    pessoas = Pessoa.objects.filter(is_active=True)

    if busca:
        pessoas = pessoas.filter(
            Q(nome__icontains=busca) |
            Q(cpf__icontains=busca)
        )

    pessoas = pessoas.order_by('nome')

    paginator = Paginator(pessoas, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page'))

    dados = {
        'tipo_relacao': '',
        'data_inicio': timezone.localdate().isoformat(),
        'data_fim': '',
        'observacoes': '',
    }

    pessoa_selecionada = None
    erros = []

    if request.method == 'POST':
        dados = {
            'tipo_relacao': request.POST.get(
                'tipo_relacao', ''
            ).strip(),
            'data_inicio': request.POST.get(
                'data_inicio', ''
            ).strip(),
            'data_fim': request.POST.get(
                'data_fim', ''
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        pessoa_id = request.POST.get('pessoa_id', '').strip()

        try:
            pessoa_selecionada = Pessoa.objects.get(
                pk=pessoa_id,
                is_active=True,
            )
        except (Pessoa.DoesNotExist, ValueError):
            erros.append('Selecione uma pessoa válida.')

        if not dados['tipo_relacao']:
            erros.append('Informe o tipo de relação.')

        try:
            data_inicio = date.fromisoformat(dados['data_inicio'])
        except (ValueError, TypeError):
            data_inicio = None
            erros.append('Informe uma data de início válida.')

        try:
            data_fim = (
                date.fromisoformat(dados['data_fim'])
                if dados['data_fim']
                else None
            )
        except (ValueError, TypeError):
            data_fim = None
            erros.append('Informe uma data de término válida.')

        if data_inicio and data_fim and data_fim < data_inicio:
            erros.append(
                'A data de término não pode ser anterior à data de início.'
            )

        if pessoa_selecionada and PessoaPet.objects.filter(
            pessoa=pessoa_selecionada,
            pet=pet,
            data_fim__isnull=True,
        ).exists():
            erros.append(
                'Esta pessoa já possui um vínculo vigente com este pet.'
            )

        if not erros:
            PessoaPet.objects.create(
                pessoa=pessoa_selecionada,
                pet=pet,
                tipo_relacao=dados['tipo_relacao'],
                data_inicio=data_inicio,
                data_fim=data_fim,
                observacoes=dados['observacoes'] or None,
            )

            messages.success(
                request,
                'Pessoa associada ao pet com sucesso.',
            )

            return redirect(
                f"{reverse('pets:editar', args=[pet.id])}?aba=pessoas"
            )

    return render(
        request,
        'pets/associar_pet_pessoa.html',
        {
            'pet': pet,
            'pessoas': page_obj.object_list,
            'busca': busca,
            'por_pagina': por_pagina,
            'page_obj': page_obj,
            'paginator': paginator,
            'dados': dados,
            'pessoa_selecionada': pessoa_selecionada,
            'erros': erros,
        },
    )
