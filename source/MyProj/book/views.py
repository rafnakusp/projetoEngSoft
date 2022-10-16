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
        if request.POST["username"] == "admin" and request.POST["password"] == "admin":
            USUARIO_LOGADO = "admin"
            return redirect("/telainicial/")
        elif request.POST["username"] == "piloto" and request.POST["password"] == "piloto":
            USUARIO_LOGADO = "piloto"
            return redirect("/telainicial/")
        elif request.POST["username"] == "torre" and request.POST["password"] == "torre":
            USUARIO_LOGADO = "torre"
            return redirect("/telainicial/")
        else:
            return render(request, "login.html")

def telainicial(request):
    template = loader.get_template('telainicial.html')
    context = {
        'username': USUARIO_LOGADO,
    }
    return HttpResponse(template.render(context, request))