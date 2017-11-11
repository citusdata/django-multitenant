from django.shortcuts import render
from django.http import HttpResponse

def index(req):
    return HttpResponse("Hi, world")
