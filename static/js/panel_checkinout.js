document.addEventListener('DOMContentLoaded', function () {
    const selectReserva = document.getElementById('selectReserva');
    const reservaDetalles = document.getElementById('reservaDetalles');
    
    // Elementos del panel de detalles
    const infoCliente = document.getElementById('infoCliente');
    const infoHabitacion = document.getElementById('infoHabitacion');
    const infoEstadia = document.getElementById('infoEstadia');
    const infoEstadoReserva = document.getElementById('infoEstadoReserva');
    
    // Botones de acción
    const btnCheckin = document.getElementById('btnCheckin');
    const btnCheckout = document.getElementById('btnCheckout');
    const btnLimpieza = document.getElementById('btnLimpieza');

    // Almacenar datos de la reserva seleccionada
    let reservaActual = {};

    // --- EVENTO: Cambiar selección de reserva ---
    selectReserva.addEventListener('change', async (e) => {
        const idReserva = e.target.value;
        if (!idReserva) {
            reservaDetalles.classList.add('hidden');
            return;
        }

        // Fetch para obtener detalles de la reserva
        const response = await fetch(`/checkinout/api/reserva/${idReserva}`);
        const data = await response.json();

        if (data.ok) {
            reservaActual = data.reserva;
            
            // Actualizar UI con los detalles
            infoCliente.textContent = `${reservaActual.nombres} ${reservaActual.apellidos}`;
            infoHabitacion.textContent = reservaActual.numero_habitacion;
            infoEstadia.textContent = `${reservaActual.fecha_entrada} a ${reservaActual.fecha_salida}`;
            
            infoEstadoReserva.textContent = reservaActual.estado_reserva;
            infoEstadoReserva.className = `status-badge status-${reservaActual.estado_reserva.toLowerCase()}`;

            // Habilitar/deshabilitar botones
            btnCheckin.disabled = reservaActual.estado_habitacion !== 'Disponible';
            btnCheckout.disabled = reservaActual.estado_habitacion !== 'Ocupada';
            btnLimpieza.disabled = reservaActual.estado_habitacion !== 'En Limpieza';

            reservaDetalles.classList.remove('hidden');
        }
    });

    // --- EVENTO: Click en Check-in ---
    btnCheckin.addEventListener('click', async () => {
        if (!reservaActual.id_reserva) return;

        const response = await fetch('/checkinout/api/checkin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_reserva: reservaActual.id_reserva,
                id_habitacion: reservaActual.id_habitacion
            })
        });
        const result = await response.json();
        if (result.ok) {
            alert(result.message);
            location.reload(); // Recargar para ver cambios
        } else {
            alert('Error al hacer check-in: ' + result.message);
        }
    });

    // --- EVENTO: Click en Check-out ---
    btnCheckout.addEventListener('click', async () => {
        if (!reservaActual.id_reserva) return;

        const response = await fetch('/checkinout/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_reserva: reservaActual.id_reserva,
                id_habitacion: reservaActual.id_habitacion
            })
        });
        const result = await response.json();
        if (result.ok) {
            alert(result.message);
            location.reload(); // Recargar para ver cambios
        } else {
            alert('Error al hacer check-out: ' + result.message);
        }
    });

    // --- EVENTO: Click en Limpieza (panel izquierdo) ---
    btnLimpieza.addEventListener('click', async () => {
        if (!reservaActual.id_habitacion) return;
        realizarLimpieza(reservaActual.id_habitacion);
    });

    // --- EVENTO: Click en Limpieza (tarjetas de habitación) ---
    document.querySelectorAll('.btn-small-limpieza').forEach(button => {
        button.addEventListener('click', async (e) => {
            const card = e.target.closest('.room-card');
            const idHabitacion = card.dataset.idHabitacion;
            realizarLimpieza(idHabitacion);
        });
    });

    async function realizarLimpieza(idHabitacion) {
        const response = await fetch('/checkinout/api/limpieza', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_habitacion: idHabitacion })
        });
        const result = await response.json();
        if (result.ok) {
            alert(result.message);
            location.reload(); // Recargar para ver cambios
        } else {
            alert('Error al marcar limpieza: ' + result.message);
        }
    }
});