from django.shortcuts import render
from .models import WeatherData

def dashboard(request):
    # Lấy dữ liệu thời tiết mới nhất
    latest_weather = WeatherData.objects.order_by('-timestamp').first()
    return render(request, 'dashboard/index.html', {'weather': latest_weather})