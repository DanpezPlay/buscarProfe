# -*- coding: utf-8 -*-

import sys, os, django
import openpyxl
import codecs
from django.utils import timezone
from datetime import datetime

sys.path.append("/path/to/buscarProfe")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buscarProfe.settings")
django.setup()

from busqueda.models import *

def migrate():
    print('Migrando CUCEI...')
    doc = openpyxl.load_workbook('UdeG.xlsx')
    hoja = doc.get_sheet_by_name('Sheet1')

    if not Cycle.objects.filter(year=2018, calendar='B').exists():
        ciclo = Cycle()
        ciclo.year = 2018
        ciclo.calendar = 'B'
        ciclo.save()
    else:
        ciclo = Cycle.objects.get(year=2018, calendar='B')
    centro = ''

    contadorFila = 0
    for fila in hoja:
        datos = {}
        if contadorFila < 5956:
            print(contadorFila)
            contador = 0
            for columna in fila:

                if contadorFila == 0:
                    if contador == 0:
                        if columna.value:
                            centro = columna.value
                            if not Center.objects.filter(name = centro).exists():
                                newCentro = Center(name=centro)
                                newCentro.save()
                            else:
                                newCentro = Center.objects.get(name=centro)

                elif contadorFila > 1:
                    # print(columna.value)
                    if contador < 14:
                        if contador == 0:
                            if columna.value:
                                # NRC
                                datos['nrc'] = columna.value

                        elif contador == 1:
                            if columna.value:
                                # clave
                                datos['clave'] = columna.value
                        elif contador == 2:
                            if columna.value:
                                # materia
                                datos['materia'] = columna.value
                        elif contador == 3:
                            if columna.value:
                                # seccion
                                datos['seccion'] = columna.value
                        elif contador == 4:
                            if columna.value:
                                # creditos
                                datos['creditos'] = columna.value
                        elif contador == 5:
                            if columna.value:
                                # maxCupos
                                datos['maxCupos'] = columna.value
                        elif contador == 6:
                            if columna.value:
                                # cupos
                                datos['cupos'] = columna.value
                        elif contador == 7:
                            if columna.value:
                                # horario
                                datos['horario'] = columna.value
                        elif contador == 8:
                            if columna.value:
                                # dias
                                datos['dias'] = columna.value
                        elif contador == 9:
                            if columna.value:
                                # edificio
                                datos['edificio'] = columna.value
                        elif contador == 10:
                            if columna.value:
                                # aula
                                datos['aula'] = columna.value
                        elif contador == 11:
                            if columna.value:
                                # periodo
                                datos['periodo'] = columna.value
                        elif contador == 12:
                            # profesor
                            if columna.value:
                                datos['nombres'] = columna.value
                        elif contador == 13:
                            if columna.value:
                                datos['apellidos'] = columna.value


                contador += 1

            print (datos)

            # Trabajar con los datos
            subject = None
            building = None
            classroom = None
            course = None
            schedule = None
            teacher = None
            day = None
            scheduleDays = None

            if 'edificio' in datos:
                if Building.objects.filter(name=datos['edificio']).exists():
                    building = Building.objects.get(name=datos['edificio'])
                else:
                    building = Building()
                    building.name = datos['edificio']
                    building.center = newCentro
                    building.save()
            #print (building)

            if 'aula' in datos and building:
                if Classroom.objects.filter(building=building, number=datos['aula'][1:], type=datos['aula'][:1]).exists():
                    classroom = Classroom.objects.get(building=building, number=datos['aula'][1:], type=datos['aula'][:1])
                else:
                    classroom = Classroom()
                    classroom.building = building
                    classroom.number = datos['aula'][1:]
                    classroom.type = datos['aula'][:1]
                    classroom.save()
            #print (classroom)

            if 'materia' in datos:
                if Subject.objects.filter(title=datos['materia']).exists():
                    subject = Subject.objects.get(title=datos['materia'])
                else:
                    subject = Subject()
                    subject.title = datos['materia']
                    if 'clave' in datos:
                        subject.key = datos['clave']
                    subject.save()
            #print (subject)

            if subject:
                if Course.objects.filter(subject=subject).exists():
                    course = Course.objects.get(subject=subject)
                else:
                    course = Course()
                    course.subject = subject
                    course.cycle = ciclo
                    course.save()
            #print (course)

            if 'nombres' in datos and 'apellidos' in datos:
                if Teacher.objects.filter(firstName = datos['nombres'], lastName = datos['apellidos']).exists():
                    teacher = Teacher.objects.get(firstName = datos['nombres'], lastName = datos['apellidos'])
                else:
                    teacher = Teacher()
                    teacher.firstName = datos['nombres']
                    teacher.lastName = datos['apellidos']
                    teacher.save()
            #print (teacher)

            # creacion del Schedule
            if 'nrc' in datos and 'seccion' in datos and 'creditos' in datos and 'maxCupos' in datos and 'cupos' in datos and 'horario' in datos and course and classroom and teacher:
                horario = datos['horario'].split('-')
                if Schedule.objects.filter(nrc = datos['nrc'], startTime=horario[0], endTime=horario[1]).exists():
                    schedule = Schedule.objects.get(nrc=datos['nrc'], startTime=horario[0], endTime=horario[1])
                else:
                    schedule = Schedule()
                    schedule.classroom = classroom
                    schedule.teacher = teacher
                    schedule.course = course
                    schedule.nrc = datos['nrc']
                    schedule.section = datos['seccion']
                    schedule.credits = datos['creditos']
                    schedule.maxQuotas = datos['maxCupos']
                    schedule.quotas = datos['cupos']
                    schedule.startTime = horario[0]
                    schedule.endTime = horario[1]
                    schedule.save()
            #print (schedule)

            if 'dias' in datos and schedule:
                datos['dias'] = datos['dias'].replace(' ',',')
                dias = datos['dias'].split(',')
                for dia in dias:
                    if Day.objects.filter(name=dia).exists():
                        day = Day.objects.get(name=dia)
                    else:
                        day = Day(name=dia)
                        day.save()

                    if day:
                        if not ScheduleDays.objects.filter(schedule=schedule, day=day).exists():
                            scheduleDays = ScheduleDays()
                            scheduleDays.schedule = schedule
                            scheduleDays.day = day
                            scheduleDays.save()
            #print (day,scheduleDays)
            #raw_input()

        contadorFila += 1
    print('CUCEI - Ok.')

def consultas():
    # nombres = ''
    # apellidos = ''
    # profesores = Teacher.objects.all()
    # for profe in profesores:
    #     nombres += profe.firstName+',\n'
    #     apellidos += profe.lastName+',\n'
    #
    # file = codecs.open('nombres.txt', 'w', 'utf-8')
    # file.write(nombres)
    # print(nombres)
    # file.close()
    #
    # file = codecs.open('apellidos.txt', 'w', 'utf-8')
    # file.write(apellidos)
    # print(apellidos)
    # file.close()
    teacher = Teacher.objects.get(firstName = 'Rebeca Del Carmen', lastName = 'Romo Vazquez')
    print (teacher)
    a = '11:30'
    schedules = Schedule.objects.filter(teacher=teacher)
    print(len(schedules))
    for schedule in schedules:
        if schedule.startTime < a and schedule.endTime > a:
            print(schedule.course.subject)


#migrate()
#consultas()

#print (timezone.localtime(timezone.now()))
import datetime

x = datetime.datetime.now()

dicdias = {'MONDAY': 'Lunes', 'TUESDAY': 'Martes', 'WEDNESDAY': 'Miercoles', 'THURSDAY': 'Jueves', 'FRIDAY': 'Viernes', 'SATURDAY': 'Sabado', 'SUNDAY': 'Domingo'}
anho = x.year
mes = x.month
dia = x.day

fecha = datetime.date(anho, mes, dia)
print (dicdias[fecha.strftime('%A').upper()])
print (str(x.time())[:5])
print(timezone.localtime())
