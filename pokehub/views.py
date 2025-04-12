from django.shortcuts import render

from auths.views import login

# Create your views here.
def main(request):
    return render(request, 'pokehub/hub.html')
