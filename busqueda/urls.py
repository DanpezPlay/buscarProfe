from django.conf.urls import url, include
from busqueda.views import  index, buscarProfesorAPI, buscarAulaAPI, buscarClaseAPI, buscarProfe, buscarClase
app_name = 'buscar'


urlpatterns = [
    url(r'^$', index),
    url(r'^buscarProfesorAPI/key=7frfsgBgYxs&firstName=(?P<firstName>.+?)&lastName=(?P<lastName>.+?)&time=(?P<time>.+?)&day=(?P<day>.+?)/$', buscarProfesorAPI, name="buscarProfesorAPI"),
    url(r'^buscarAulaAPI/key=7frfsgBgYxs&building=(?P<building>.+?)&classroom=(?P<classroom>.+?)&time=(?P<time>.+?)&day=(?P<day>.+?)/$', buscarAulaAPI, name="buscarAulaAPI"),
    url(r'^buscarClaseAPI/key=7frfsgBgYxs&subject=(?P<subject>.+?)&time=(?P<time>.+?)&day=(?P<day>.+?)/$', buscarClaseAPI, name="buscarClaseAPI"),
    url(r'^buscarProfe/$', buscarProfe, name="buscarProfe"),
    url(r'^buscarClase/$', buscarClase, name="buscarClase")
]