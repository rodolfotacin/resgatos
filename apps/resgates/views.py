from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse

from apps.pets.models import Pet
from .models import Resgate


@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    resgates = Resgate.objects.filter(
        is_active=True
    ).select_related(
        'pet'
    ).order_by(
        '-data_resgate',
        '-id',
    )

    if busca:
        resgates = resgates.filter(
            Q(pet__nome__icontains=busca)
            | Q(local__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(observacoes__icontains=busca)
        )

    paginator = Paginator(resgates, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(
        request,
        'resgates/lista.html',
        {
            'resgates': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'busca': busca,
            'por_pagina': por_pagina,
        },
    )


def obter_pets_para_formulario(resgate=None):
    """
    Lista pets ativos para novos resgates.
    Na edição, também mantém disponível o pet já vinculado,
    mesmo que tenha sido inativado.
    """
    pets = Pet.objects.filter(is_active=True)

    if resgate:
        pets = Pet.objects.filter(
            models_q_pet(resgate.pet_id)
        ) | pets

    return pets.order_by('nome').distinct()


def models_q_pet(pet_id):
    from django.db.models import Q
    return Q(pk=pet_id)


def dados_resgate(resgate=None):
    if not resgate:
        return {
            'pet_id': '',
            'data_resgate': '',
            'local': '',
            'descricao': '',
            'observacoes': '',
            'is_active': True,
        }

    return {
        'pet_id': str(resgate.pet_id),
        'data_resgate': timezone.localtime(
            resgate.data_resgate
        ).strftime('%Y-%m-%dT%H:%M'),
        'local': resgate.local,
        'descricao': resgate.descricao or '',
        'observacoes': resgate.observacoes or '',
        'is_active': resgate.is_active,
    }


@login_required
def adicionar(request):
    origem = request.GET.get('origem', '')

    if request.method == 'POST':
        origem = request.POST.get('origem', '')

    dados = dados_resgate()

    # Se o cadastro começou pelo Pet, preenche o Pet automaticamente.
    pet_id = (
        request.POST.get('pet_id', '').strip()
        if request.method == 'POST'
        else request.GET.get('pet_id', '').strip()
    )

    if pet_id:
        dados['pet_id'] = pet_id

    if request.method == 'POST':
        dados = {
            'pet_id': request.POST.get('pet_id', '').strip(),
            'data_resgate': request.POST.get(
                'data_resgate', ''
            ).strip(),
            'local': request.POST.get('local', '').strip(),
            'descricao': request.POST.get('descricao', '').strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
            'is_active': True,
        }

        obrigatorios = ['pet_id', 'data_resgate', 'local']

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )
        else:
            try:
                pet = Pet.objects.get(
                    pk=dados['pet_id'],
                    is_active=True,
                )

                data_resgate = datetime.strptime(
                    dados['data_resgate'],
                    '%Y-%m-%dT%H:%M',
                )

                data_resgate = timezone.make_aware(
                    data_resgate,
                    timezone.get_current_timezone(),
                )

                resgate = Resgate.objects.create(
                    pet=pet,
                    data_resgate=data_resgate,
                    local=dados['local'],
                    descricao=dados['descricao'] or None,
                    observacoes=dados['observacoes'] or None,
                    is_active=True,
                )

                messages.success(
                    request,
                    'Resgate registrado com sucesso.'
                )

                if origem == 'pet':
                    return redirect(
                        f"{reverse('pets:editar', args=[resgate.pet_id])}?aba=resgates"
                    )

                return redirect('resgates:lista')

            except Pet.DoesNotExist:
                messages.error(
                    request,
                    'Selecione um Pet ativo válido.'
                )
            except ValueError:
                messages.error(
                    request,
                    'Informe um Pet e uma data e hora válidos.'
                )

    return render(
        request,
        'resgates/formulario.html',
        {
            'dados': dados,
            'pets': obter_pets_para_formulario(),
            'origem': origem,
        }
    )



@login_required
def editar(request, resgate_id):
    resgate = get_object_or_404(
        Resgate.objects.select_related('pet'),
        pk=resgate_id,
    )

    # Preserva o contexto de origem durante toda a edição.
    origem = (
        request.POST.get('origem', request.GET.get('origem', ''))
        if request.method == 'POST'
        else request.GET.get('origem', '')
    )

    contexto_pet_id = (
        request.POST.get(
            'contexto_pet_id',
            request.GET.get('pet_id', ''),
        ).strip()
    )

    dados = dados_resgate(resgate)

    # Na abertura pelo contexto do Pet, mantém o Pet selecionado.
    if request.method == 'GET' and contexto_pet_id:
        try:
            pet = Pet.objects.get(
                pk=contexto_pet_id,
                is_active=True,
            )
            dados['pet_id'] = str(pet.id)
        except (Pet.DoesNotExist, ValueError):
            pass

    if request.method == 'POST':
        dados = {
            'pet_id': request.POST.get('pet_id', '').strip(),
            'data_resgate': request.POST.get(
                'data_resgate', ''
            ).strip(),
            'local': request.POST.get('local', '').strip(),
            'descricao': request.POST.get('descricao', '').strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
            'is_active': resgate.is_active,
        }

        obrigatorios = ['pet_id', 'data_resgate', 'local']

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )
        else:
            try:
                pet = Pet.objects.get(pk=dados['pet_id'])

                # Permite manter o Pet atual, mesmo inativo,
                # mas não trocar para outro Pet inativo.
                if not pet.is_active and pet.pk != resgate.pet_id:
                    raise Pet.DoesNotExist

                data_resgate = datetime.strptime(
                    dados['data_resgate'],
                    '%Y-%m-%dT%H:%M',
                )
                data_resgate = timezone.make_aware(
                    data_resgate,
                    timezone.get_current_timezone(),
                )

                resgate.pet = pet
                resgate.data_resgate = data_resgate
                resgate.local = dados['local']
                resgate.descricao = dados['descricao'] or None
                resgate.observacoes = dados['observacoes'] or None
                resgate.save()

                messages.success(
                    request,
                    'Resgate atualizado com sucesso.'
                )

                if origem == 'pet' and contexto_pet_id:
                    return redirect(
                        f"{reverse('pets:editar', args=[contexto_pet_id])}"
                        "?aba=resgates"
                    )

                return redirect(
                    'resgates:editar',
                    resgate_id=resgate.id,
                )

            except Pet.DoesNotExist:
                messages.error(
                    request,
                    'Selecione um Pet ativo válido.'
                )
            except ValueError:
                messages.error(
                    request,
                    'Informe uma data e hora válidas.'
                )

    return render(
        request,
        'resgates/formulario.html',
        {
            'resgate': resgate,
            'dados': dados,
            'pets': obter_pets_para_formulario(resgate),
            'origem': origem,
            'contexto_pet_id': contexto_pet_id,
        },
    )


@login_required
@require_POST
def inativar(request, resgate_id):
    resgate = get_object_or_404(Resgate, pk=resgate_id)

    origem = request.POST.get('origem', '')
    contexto_pet_id = request.POST.get('contexto_pet_id', '').strip()

    if not resgate.is_active:
        messages.warning(
            request,
            'Este resgate já está inativo.'
        )
    else:
        resgate.is_active = False
        resgate.save(update_fields=['is_active', 'updated_at'])

        messages.success(
            request,
            'Resgate inativado com sucesso.'
        )

    if origem == 'pet' and contexto_pet_id:
        return redirect(
            f"{reverse('pets:editar', args=[contexto_pet_id])}"
            "?aba=resgates"
        )

    return redirect('resgates:lista')
