from django.contrib import admin
from django.urls import path
from my_polls import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota para geração da descrição CHA, esperando como POST cargo e nivel.
    path('chat', views.chatgpt, name='chatgpt'),

    # Rota para raspar os curriculos de acordo com a descrição gerada, não esperando nenhum parametro.
    path('scrap', views.scrap, name='scrap'),

    # Rota para fazer o match dos candidatos ja retornando o rank dos 8 melhores, esperando os cadidatos e a descrição CHA.
    path('match', views.match, name='match'),
        
    # Rota para aprimoramento da descrição CHA, esperando como POST cargo, nivel, cha, campo e descricao (opcional).
    path('upgrade', views.upgrade, name='upgrade'),

]
