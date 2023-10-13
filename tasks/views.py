from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Task

# RENDERIZAR EL INICIO
def home(request):
    return render(request, 'home.html')

# RENDERIZAR Y DIRIGIR A INSCRIBIRSE 
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            "form": UserCreationForm
        })
    
    else:
        # VALIDACION DE CONTRASEÑA Y CONFIRMACION
        if request.POST["password1"] == request.POST["password2"]:
            try:

                #REGISTRAR USUARIO
                user = User.objects.create_user(

                    request.POST["username"], password=request.POST["password1"])
                
                # GUARDAR USUARIO Y MANTENER SESION
                user.save()
                login(request, user)
                return redirect('tasks')
            
            # EN CASO DE HABER ERRORES DE INTEGRACION DEL FORMULARIO
            except IntegrityError:

                return render(request, 'signup.html', {
                    "form": UserCreationForm,
                    "error": "El usuario ya existe."
                })

        return render(request, 'signup.html', {
            "form": UserCreationForm, 
            "error": "Las contraseñas no coinciden."
        })



# REDIRIGIR A ACTIVIDADES AL INICIAR SESION
@login_required
def tasks(request):
    # MOSTRAR ACTIVIDADES QUE NO TIENEN FECHA DE COMPLETADO
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {
        "tasks": tasks
    })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {
        "tasks": tasks
    })

# REDIRIGIR A LA CREACION DE ACTIVIDADES
@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {
            "form": TaskForm
        })
    else:
        try:
            # GUARDAR ACTIVIDADES CREADAS
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()

            return redirect('tasks')
        
        # EN CASO DE HABER UN ERROR AL CREAR LA ACTIVIDAD
        except ValueError:
            return render(request, 'create_task.html', {
                "form": TaskForm,
                "error": "Hubo un error al crear la actividad."
            })




@login_required
def signout(request):
    logout(request)
    return redirect('home')

#  AUTENTICACION DE INICIO DE SESION
def signin(request):

    if request.method == 'GET':
        return render(request, 'signin.html', {
            "form": AuthenticationForm
        })
    
    # EN CASO DE NO PODER INICIAR SESION
    else:

        # AUTENTICACION & VALIDACION
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        
        # SI NO EXISTE EL USUARIO O ERROR DE TYPING
        if user is None:
            return render(request, 'signin.html', {
                "form": AuthenticationForm, 
                "error": "El usuario o la contraseña es incorrecta."
            })

        login(request, user)
        return redirect('tasks')


# RENDERIZAR Y REDIRIGIR A DETALLES DE ACTIVIDADES
@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task, 
            'form': form
        })
    
    
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task, 
                'form': form, 
                'error': 'Error al actualizar la actividad.'
            })

# RENDERIZAR Y REDIRIGIR A ACTIVIDADES COMPLETADAS
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
    

# RENDERIZAR Y REDIRIGIR A TAREAS BORRADAS??
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')