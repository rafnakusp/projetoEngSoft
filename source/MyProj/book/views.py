from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader

USUARIO_LOGADO = ""
CONTAGEM_DE_FALHAS_NO_LOGIN = 0

@csrf_exempt
def bookview(request):
    global CONTAGEM_DE_FALHAS_NO_LOGIN
    print("==========================================")
    print(request.method)
    print(request.POST)
    
    if CONTAGEM_DE_FALHAS_NO_LOGIN >= 3:
        return render(request, "loginbloqueado.html")

    if request.method == "GET":
        global USUARIO_LOGADO
        return render(request, "login.html")

    elif request.method == "POST":
        if request.POST["username"] == "operadordevoos" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "operadordevoos"
        elif request.POST["username"] == "usuariostatus" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "usuariostatus"
        elif request.POST["username"] == "gerentedeoperacoes" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "gerentedeoperacoes"        
        
        else:
            CONTAGEM_DE_FALHAS_NO_LOGIN += 1
            if CONTAGEM_DE_FALHAS_NO_LOGIN >= 3:
                return render(request, "loginbloqueado.html")
            return render(request, "login.html")

        CONTAGEM_DE_FALHAS_NO_LOGIN = 0
        return redirect("/telainicial/")

def telainicial(request):
    template = loader.get_template('telainicial.html')
    context = {
        'username': USUARIO_LOGADO,
    }
    return HttpResponse(template.render(context, request))

def crud(request):
    return render(request, "crud.html")

def monitoramentodevoos(request):
    return render(request, "monitoramentodevoos.html")

def geracaoderelatorios(request):
    return render(request, "geracaoderelatorios.html")

################################################################################
####                               CRUD de voos                             ####
################################################################################

################################################################################
####          Atualizar o status de voos/ Painel de Monitoração             ####
################################################################################

class PainelDeMonitoracao():
    pass

################################################################################
####                            Geração de relatório                        ####
################################################################################