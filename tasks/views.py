from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db  import IntegrityError
from django.utils import timezone
from .forms import TaskForm
from .models import Task

import os
from pymongo import MongoClient
import datetime
from django.http import JsonResponse

# Create your views here.
def helloworld(request):
    return render(request, 'signup.html', {'form': UserCreationForm})

def home(request):
    return render(request, 'home.html')

def signup(request):
    
    if request.method == "GET":
        return render(request, 'signup.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {'form': UserCreationForm, 'error': 'Username already exists'})
        else:
            return render(request, 'signup.html', {'form': UserCreationForm, 'error': 'Password do not match'})

@login_required
def tasks(request):
    conexion()
    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_complete(request):
    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=False).order_by('-datacompleted')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_detail(request,task_id):
    if request.method == "GET":
        tasks = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=tasks)
        return render(request, 'task_detail.html', {'task': tasks, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': tasks, 'form': form ,'error': "Error updating task"})

@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.datacompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required    
def delete_task(request,task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":        
        task.delete()
        return redirect('tasks')
    

##
# Creamos la conexion

def conexion():
    client = MongoClient('mongodb+srv://user:Admin456@atlascluster.fgujvv6.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster')  # Cambia la URI según tu configuración
    db = client['DB_final']
    coleccion = db['documentos']
    # Obtener un documento de la colección (puedes usar el primero)
    documento = coleccion.find_one()

    # Obtener los nombres de los campos del documento
    nombres_campos = list(documento.keys())

    # Imprimir los nombres de los campos
    print(nombres_campos)
    return coleccion

def CargarAnos():
    coleccion = conexion()
    valores_unicos = coleccion.distinct("AnoPublicacion")
    valores_unicos = set(valores_unicos)
    AnoPublicacion = list(valores_unicos)
    return AnoPublicacion

def CargarTipo(request):
    print("CargarTipo")
    if request.method == 'GET':        
        seleccion = request.GET.get('seleccion')
       
        coleccion = conexion()
        resultados = coleccion.find({"AnoPublicacion": seleccion},{"_id": 0,  "Tipo": 1})
        
        # Obtener valores únicos del campo 'Tipo' de los resultados
        valores_unicos = set()

        for documento in resultados:
            valores_unicos.add(documento['Tipo'])

        # Convertir los valores únicos en una lista
        tipos = list(valores_unicos)
        return JsonResponse(tipos, safe=False)
    else:
        # Manejar caso si no se proporciona una opción válida
        tipos = []

        # Devolver los datos como respuesta en formato JSON
        return JsonResponse(tipos, safe=False)

def CargarFechaPublicacion(request):
    print("CargarFechaPublicacion")
    if request.method == 'GET':        
        ano = request.GET.get('ano')
        tipo = request.GET.get('tipo')
       
        coleccion = conexion()
        resultados = coleccion.find({"AnoPublicacion": ano, "Tipo": tipo},{"_id": 0,  "FechaPublicacion": 1})
        
        # Obtener valores únicos del campo 'Tipo' de los resultados
        valores_unicos = set()

        for documento in resultados:
            valores_unicos.add(documento['FechaPublicacion'])

        # Convertir los valores únicos en una lista
        fechas = list(valores_unicos)
        return JsonResponse(fechas, safe=False)
    else:
        # Manejar caso si no se proporciona una opción válida
        fechas = []

        # Devolver los datos como respuesta en formato JSON
        return JsonResponse(fechas, safe=False)
    
def CargarProvincia(request):
    print("CargarProvincia")
    if request.method == 'GET':        
        ano = request.GET.get('ano')
        tipo = request.GET.get('tipo')
        fecha = request.GET.get('fecha')
       
        coleccion = conexion()
        resultados = coleccion.find({"AnoPublicacion": ano, "Tipo": tipo, "FechaPublicacion":fecha},{"_id": 0,  "NombreProvidencia": 1})
        
        # Obtener valores únicos del campo 'Tipo' de los resultados
        valores_unicos = set()

        for documento in resultados:
            print(documento['NombreProvidencia'])
            valores_unicos.add(documento['NombreProvidencia'])

        # Convertir los valores únicos en una lista
        provincias = list(valores_unicos)
        return JsonResponse(provincias, safe=False)
    else:
        # Manejar caso si no se proporciona una opción válida
        provincias = []

        # Devolver los datos como respuesta en formato JSON
        return JsonResponse(provincias, safe=False)
    
def CargarConsulta(request):
    print("CargarConsulta")
    if request.method == 'GET':        
        seleccion = request.GET.get('seleccion')
        print(f"seleccion : {seleccion}")
        coleccion = conexion()
        print("1")
        resultados = coleccion.find({"NombreProvidencia": seleccion})
        print("2")
        # Convertir los ObjectId a strings para que puedan ser serializados a JSON
        lista_resultados = []
        for resultado in resultados:
            # Convertir el ObjectId a string
            resultado['_id'] = str(resultado['_id'])
            lista_resultados.append(resultado)

        return JsonResponse(lista_resultados, safe=False)
    else:
        # Manejar caso si no se proporciona una opción válida
        consulta = []

        # Devolver los datos como respuesta en formato JSON
        return JsonResponse(consulta, safe=False)
##

@login_required
def create_task(request):
    if request.method =="POST":
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html' , { 'form': TaskForm, 'error': 'Please provide valida data'})
    else:
        anos = CargarAnos()
        return render(request, 'create_task.html' , { 'form': TaskForm , 'anos': anos})

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html',{'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'] )
        if user is None:
            return render(request, 'signin.html',{'form': AuthenticationForm,'error': 'Username or password is incorrect'})
        else:
            login(request, user)
            return redirect('tasks')
        
@login_required
def codigo(request):
    return render(request, 'codigo.html')    