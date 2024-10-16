import requests

def obtener_datos_tabla():
    # URL api OpenWeatherMap
    url = "https://api.openweathermap.org/data/2.5/forecast"
    city_id = "3111107"  # ID Salamanca
    api_key = "" 

    # solicitud GET
    params = {
        "id": city_id,
        "appid": api_key,
        "units": "metric",  # Celsius
    }

    # get a OpenWeatherMap
    response = requests.get(url, params=params)

    # Verificar si piola
    if response.status_code == 200:
        # datos en JSON
        data = response.json()
        tabla = []

        # Iterar sobre los datos de pronóstico para los próximos 7 días
        for forecast in data["list"][:7]:
            date_time = forecast["dt_txt"]
            temperature = forecast["main"]["temp"]
            description = forecast["weather"][0]["description"]
            rain_probability = forecast.get("pop", 0) * 100
            
            # Agregar los datos del pronóstico a la lista
            tabla.append({
                "date_time": date_time,
                "temperature": temperature,
                "description": description,
                "rain_probability": rain_probability
            })

        return tabla
    else:
        print("Error al obtener el pronóstico del tiempo:", response.status_code)
