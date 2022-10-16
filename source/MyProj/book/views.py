from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader

USUARIO_LOGADO = ""

@csrf_exempt
def bookview(request):
    print("==========================================")
    print(request.method)
    print(request.POST)
    
    if request.method == "GET":
        global USUARIO_LOGADO
        return render(request, "login.html")
    elif request.method == "POST":
        if request.POST["username"] == "operadordevoos" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "operadordevoos"
            return redirect("/telainicial/")
        elif request.POST["username"] == "usuariostatus" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "usuariostatus"
            return redirect("/telainicial/")
        elif request.POST["username"] == "gerentedeoperacoes" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "gerentedeoperacoes"
            return redirect("/telainicial/")
        else:
            return render(request, "login.html")

def telainicial(request):
    template = loader.get_template('telainicial.html')
    context = {
        'username': USUARIO_LOGADO,
    }
    return HttpResponse(template.render(context, request))