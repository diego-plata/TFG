async function obtenerColeccionesDeDispositivosRegistrados() {
    try {
        // solicitar a server las colecciones de dispositivos registrados
        const response = await fetch('/obtener_dispositivos_registrados_id'); // ruta en el servidor

        // ver si éxito
        if (!response.ok) {
            throw new Error('No colecciones de dispositivos registrados.');
        }

        // de la respuesta sacamos colecciones
        const colecciones = await response.json();

        
        return colecciones;
    } catch (error) {
        // Manejar errores
        console.error('Error al obtener las colecciones de dispositivos registrados:', error);
        throw error;
    }
}

function mostrarColeccionesEnTabla(colecciones) {
    try {
        // Seleccionar el contenedor de dispositivos en el html
        const dispositivosContainer = document.getElementById("dispositivos-container");

        // Crear una tabla HTML
        const tablaHTML = document.createElement("table");
        tablaHTML.border = '5';

        // Crear primera fila de la tabla con encabezados
        const headerRow = tablaHTML.insertRow();
        const headers = ["Nombre de la colección"];
        headers.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            headerRow.appendChild(th);
        });

        // Iterar sobre colecciones y agregar filas a la tabla
        Object.keys(colecciones).forEach(key => {
            const dispositivos = colecciones[key].split(','); // Dividir los dispositivos registrados por coma
            dispositivos.forEach(dispositivo => {
                const row = tablaHTML.insertRow(); // Crear una fila para cada dispositivo
                const cell = row.insertCell();
                const link = document.createElement("a");
                link.href = "colecciones/dispositivos.html?nombre=" + encodeURIComponent(dispositivo.trim()); // Pasar el nombre del dispositivo como parámetro de consulta en la URL
                link.textContent = dispositivo.trim();
                cell.appendChild(link);
            });
        });
        
        // Limpiar el contenedor de dispositivos
        dispositivosContainer.innerHTML = "";

        // Agregar la tabla al contenedor en el HTML
        dispositivosContainer.appendChild(tablaHTML);
    } catch (error) {
        // Manejar errores
        console.error('Error al mostrar las colecciones en la tabla:', error);
        throw error;
    }
}


// obtener y mostrar las colecciones en la tabla
async function obtenerYMostrarColeccionesDeDispositivosRegistrados() {
    try {
        // Obtener las colecciones de dispositivos registrados desde el servidor 
        const colecciones = await obtenerColeccionesDeDispositivosRegistrados();

        // Mostrar las colecciones en la tabla HTML
        mostrarColeccionesEnTabla(colecciones);
    } catch (error) {
        // Manejar errores
        console.error('Error en la función principal:', error);
    }
}

// Llamar a la función principal para obtener y mostrar las colecciones al cargar la página
obtenerYMostrarColeccionesDeDispositivosRegistrados();
