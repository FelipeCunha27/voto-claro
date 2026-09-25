from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registrar(requisicao):
    if requisicao.method == "POST":
        formulario = RegistroForm(requisicao.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            login(requisicao, usuario)
            return redirect("/")
    else:
        formulario = RegistroForm()
        
    return render(requisicao, "accounts/registrar.html", {"form": formulario})
