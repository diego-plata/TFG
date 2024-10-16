async function obtenerYMostrarDatosTabla(ciudad) {
    try {
        const apiKey = 'e27a2065ccfe1b3bbdf9ddcb44fbe220'; 
        const units = 'metric';    // celsius
        const apiUrl = `https://api.openweathermap.org/data/2.5/forecast?q=${ciudad}&appid=${apiKey}&units=${units}`;

        // Realizar la solicitud a la API
        const response = await fetch(apiUrl);

        // Verificar si la solicitud fue exitosa (código de estado HTTP 200)
        if (!response.ok) {
            throw new Error('No se pudo obtener el pronóstico del tiempo.');
        }

        // Convertir la respuesta a formato JSON
        const data = await response.json();

        // Seleccionar el elemento HTML donde deseas mostrar la tabla
        const tablaContainer = document.getElementById("tabla-container");

        // Limpia cualquier contenido previo
        tablaContainer.innerHTML = "";

        // Crear una tabla HTML
        const tablaHTML = document.createElement("table");
        tablaHTML.border = '1';

        // Crear la fila de encabezado
        const headerRow = tablaHTML.insertRow();
        const headers = ["Fecha y hora", "Temperatura (°C)", "Sensación térmica (°C)", "Mínima (°C)", "Máxima (°C)", "Presión (hPa)", "Humedad (%)", "Velocidad del viento (m/s)", "Nubosidad (%)", "Probabilidad de lluvia (%)"];
        headers.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            headerRow.appendChild(th);
        });

       
        data.list.slice(0, 7).forEach(forecast => {
            const row = tablaHTML.insertRow();
            row.insertCell().textContent = forecast.dt_txt;
            row.insertCell().textContent = forecast.main.temp;
            row.insertCell().textContent = forecast.main.feels_like;
            row.insertCell().textContent = forecast.main.temp_min;
            row.insertCell().textContent = forecast.main.temp_max;
            row.insertCell().textContent = forecast.main.pressure;
            row.insertCell().textContent = forecast.main.humidity;
            row.insertCell().textContent = forecast.wind.speed;
            row.insertCell().textContent = forecast.clouds.all;
            //row.insertCell().textContent = forecast.weather[0].description;
            row.insertCell().textContent = (forecast.pop || 0) * 100;
        });

        // Agregar la tabla al contenedor en el HTML
        tablaContainer.appendChild(tablaHTML);

    } catch (error) {
        // Manejar los errores
        console.error('Error al obtener el pronóstico del tiempo:', error.message);
    }
}


function actualizarPronostico() {
    const ciudad = document.getElementById('city-input').value;
    var cityTitle = document.getElementById("city-title"); // Obtener el elemento con id "city-title"
    obtenerYMostrarDatosTabla(ciudad); 
    // Actualizar el texto del elemento con el nuevo pronóstico
    cityTitle.textContent = "Pronóstico para " + ciudad;
}


obtenerYMostrarDatosTabla('Salamanca'); // por defecto Salamanca
