# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from busqueda.models import Center, Building, Classroom, Cycle, Subject, Course, Teacher, Day, Schedule, ScheduleDays
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, date
import json

dicdias = {'MONDAY': 'Lunes', 'TUESDAY': 'Martes', 'WEDNESDAY': 'Miercoles', 'THURSDAY': 'Jueves',
               'FRIDAY': 'Viernes', 'SATURDAY': 'Sabado', 'SUNDAY': 'Domingo'}
numbers = ['1','2','3','4','5','6','7','8','9','0']


#x = datetime.now()
x = timezone.localtime()
anho = x.year
mes = x.month
dia = x.day
fecha = date(anho, mes, dia)
today = dicdias[fecha.strftime('%A').upper()]

# Create your views here.
def index(request):
    return render(request, 'index.html')

def buscarProfesorAPI(request, firstName, lastName, time, day):
    if firstName != 'NP' and lastName != 'NP':
        teacher = Teacher.objects.get(firstName=firstName, lastName=lastName)
    elif firstName != 'NP':
        teacher = Teacher.objects.filter(firstName=firstName)
        if len(teacher) > 1:
            return JsonResponse({'response':'error','details':'Se encontro mas de un profesor, especifica nombres y apellidos'})
        else:
            teacher = teacher[0]
    elif lastName != 'NP':
        teacher = Teacher.objects.filter(lastName=lastName)
        if len(teacher) > 1:
            return JsonResponse({'response':'error','details':'Se encontro mas de un profesor, especifica nombres y apellidos'})
        else:
            teacher = teacher[0]

    if time == 'NP':
        time = str(x.time())[:5]
    if day == 'NP':
        day = today

    day = Day.objects.get(name=day)

    schedules = Schedule.objects.filter(teacher=teacher)
    for schedule in schedules:
        if schedule.startTime <= time and schedule.endTime >= time:
            if ScheduleDays.objects.filter(day=day, schedule=schedule).exists():

                contexto = {'response':'success', 'teacher':teacher.firstName + ' ' + teacher.lastName, 'startTime':schedule.startTime, 'endTime':schedule.endTime, 'day':day.name, 'subject':schedule.course.subject.title, 'building':schedule.classroom.building.name.lstrip('DE'), 'number':schedule.classroom.number.lstrip('0'), 'type':schedule.classroom.type}

                return JsonResponse(contexto)

    return JsonResponse({'response':'notFound','details':'No se encontro una clase asignada al profesor con los datos proporcionados'})

def buscarAulaAPI(request, building, classroom, time, day):
    if time == 'NP':
        time = str(x.time())[:5]
    if day == 'NP':
        day = today

    day = Day.objects.get(name=day)

    if building == 'UCT1' or building == 'UCT2':
        building = 'D'+building
    elif len(building) == 1:
        building = 'DED'+building.upper()
    else:
        return JsonResponse({'response':'error','details':'El edificio no tiene el formato aceptado (X, Y, UCT1, etc.)'})

    if Building.objects.filter(name=building).exists():
        buildings = Building.objects.filter(name=building)
        if len(buildings) > 1:
            return JsonResponse({'response': 'error', 'details': 'Se encontro mas de un edificio con ese nombre'})
        else:
            building = buildings[0]
    else:
        return JsonResponse({'response': 'error', 'details': 'No se encontro el edificio especificado'})

    if Classroom.objects.filter(building=building).exists():
        classrooms = Classroom.objects.filter(building=building)
        for classr in classrooms:
            number = ''
            for d in classr.number:
                if d in numbers:
                    number+=d
            number = str(int(number))
            if classroom == number:
                schedules = Schedule.objects.filter(classroom=classr)
                for schedule in schedules:
                    if schedule.startTime <= time and schedule.endTime >= time:
                        if ScheduleDays.objects.filter(day=day, schedule=schedule).exists():
                            contexto = {
                                'response': 'success', 'teacher': schedule.teacher.firstName + ' ' + schedule.teacher.lastName,
                                'startTime': schedule.startTime, 'endTime': schedule.endTime, 'day':day.name,
                                'subject': schedule.course.subject.title, 'building': schedule.classroom.building.name.lstrip('DE'),
                                'number': classroom.lstrip('0')
                            }
                            return JsonResponse(contexto)

    return JsonResponse({'response':'notFound','details':'No se encontro alguna clase en el aula especificada'})

def buscarClaseAPI(request, subject, time, day):
    if time == 'NP':
        time = str(x.time())[:5]
    if day == 'NP':
        day = today

    day = Day.objects.get(name=day)

    clases = []

    subject = subject.title()

    if Subject.objects.filter(title=subject).exists():
        sub = Subject.objects.filter(title=subject)
        for s in sub:
            if Course.objects.filter(subject=s).exists():
                courses = Course.objects.filter(subject=s)
                for course in courses:
                    if Schedule.objects.filter(course=course).exists():
                        schedules = Schedule.objects.filter(course=course)
                        for schedule in schedules:
                            if schedule.startTime <= time and schedule.endTime >= time:
                                if ScheduleDays.objects.filter(day=day).exists():
                                    datos = {
                                        'teacher': schedule.teacher.firstName + ' ' + schedule.teacher.lastName,
                                        'startTime': schedule.startTime, 'endTime': schedule.endTime, 'day':day.name,
                                        'subject': schedule.course.subject.title,
                                        'building': schedule.classroom.building.name.lstrip('DE'),
                                        'number': schedule.classroom.number.lstrip('0')
                                    }
                                    clases.append(datos)
    if clases:
        return JsonResponse({'response':'success', 'classrooms':clases})
    else:
        return JsonResponse({'response':'notFound','details':'No se pudo encontrar ninguna clase de la materia especificada'})

def buscarProfe(request):
    if request.method == 'POST':
        nombres = request.POST.get('nombres')
        dia = request.POST.get('dia')
        hora = request.POST.get('horario')

        if dia:
            #return JsonResponse({'dia':dia})
            dia = dia.split('-')
            dia = date(int(dia[0]), int(dia[1]), int(dia[2]))
            dia = dicdias[dia.strftime('%A').upper()]
        else:
            dia = today

        dia = Day.objects.get(name=dia)

        if not hora:
            hora = str(x.time())[:5]


        if nombres:
            nombres = nombres.title()
            maestros = []
            maestro = ''
            teachers = Teacher.objects.all()
            for teacher in teachers:
                nameTeacher = teacher.firstName + ' ' + teacher.lastName
                if nombres in nameTeacher:
                    schedules = Schedule.objects.filter(teacher=teacher)
                    for schedule in schedules:
                        if schedule.startTime <= hora and schedule.endTime >= hora:
                            if ScheduleDays.objects.filter(day=dia, schedule=schedule).exists():
                                data = {'teacher': teacher.firstName + ' ' + teacher.lastName,
                                            'startTime': schedule.startTime, 'endTime': schedule.endTime, 'day': dia.name,
                                            'subject': schedule.course.subject.title, 'building': schedule.classroom.building.name,
                                            'number': schedule.classroom.number, 'type': schedule.classroom.type}
                                maestro = data['teacher']
                                maestros.append(data)
            if maestros:
                return render(request, 'profe.html', {'maestros':maestros, 'maestro':maestro})

        return render(request, 'index.html', {'profeNotFound':nombres+hora})

def buscarClase(request):
    if request.method == 'POST':
        edificio = request.POST.get('edificio')
        aula = request.POST.get('aula')
        dia = request.POST.get('dia')
        hora = request.POST.get('horario')

        if dia:
            #return JsonResponse({'dia':dia})
            dia = dia.split('-')
            dia = date(int(dia[0]), int(dia[1]), int(dia[2]))
            dia = dicdias[dia.strftime('%A').upper()]
        else:
            dia = today

        dia = Day.objects.get(name=dia)

        if not hora:
            hora = str(x.time())[:5]


        if edificio and aula:
            edificio = edificio.upper()
            if edificio == 'UCT1' or edificio == 'UCT2':
                edificio = 'D' + edificio
            elif len(edificio) == 1:
                edificio = 'DED' + edificio.upper()

            clase = {}
            building = Building.objects.get(name=edificio)
            clasrooms = Classroom.objects.filter(building=building)
            for classr in clasrooms:
                number = ''
                for d in classr.number:
                    if d in numbers:
                        number += d
                number = str(int(number))
                if aula == number:
                    if Schedule.objects.filter(classroom=classr).exists():
                        schedules = Schedule.objects.filter(classroom=classr)
                        for schedule in schedules:
                            if schedule.startTime <= hora and schedule.endTime >= hora:
                                if ScheduleDays.objects.filter(day=dia, schedule=schedule).exists():
                                    data = {'teacher': schedule.teacher.firstName + ' ' + schedule.teacher.lastName,
                                                'startTime': schedule.startTime, 'endTime': schedule.endTime, 'day': dia.name,
                                                'subject': schedule.course.subject.title, 'building': schedule.classroom.building.name,
                                                'number': schedule.classroom.number, 'type': schedule.classroom.type}
                                    clase = data
            if clase:
                return render(request, 'clase.html', {'clase':clase})

        return render(request, 'index.html', {'claseNotFound':edificio + ' - ' + aula})