document.addEventListener("DOMContentLoaded", () => {
    const roomModalEl = document.getElementById('roomModal');
    const roomModal = new bootstrap.Modal(roomModalEl);
    const modalTitle = document.getElementById('modalTitle');
    const roomForm = document.getElementById('roomForm');
    const roomIdInput = document.getElementById('roomId');

    // Función para poblar el select de tipos de habitación
    async function populateRoomTypes() {
        const roomTypeSelect = document.getElementById('roomType');
        roomTypeSelect.innerHTML = '<option value="">Cargando tipos...</option>';
        try {
            const response = await fetch('/habitaciones/api/tipos_habitacion');
            const tipos = await response.json();
            roomTypeSelect.innerHTML = '<option value="">Seleccionar tipo...</option>';
            tipos.forEach(tipo => {
                roomTypeSelect.innerHTML += `<option value="${tipo.id_tipo}">${tipo.nombre}</option>`;
            });
        } catch (error) {
            roomTypeSelect.innerHTML = '<option value="">Error al cargar</option>';
        }
    }

    // 1. Abrir modal para CREAR
    const btnCrear = document.querySelector('button[data-bs-target="#roomModal"]');
    btnCrear.addEventListener('click', async () => {
        modalTitle.textContent = 'Crear Nueva Habitación';
        roomForm.reset();
        roomIdInput.value = '';
        await populateRoomTypes();
        roomModal.show();
    });

    // 2. Abrir modal para EDITAR
    window.openEditDialog = async (id) => {
        modalTitle.textContent = 'Editar Habitación';
        roomForm.reset();
        roomIdInput.value = id;

        await populateRoomTypes(); // Poblar tipos antes de seleccionar

        try {
            const response = await fetch(`/habitaciones/obtener/${id}`);
            if (!response.ok) throw new Error('No se pudieron cargar los datos.');
            const data = await response.json();

            document.getElementById('roomNumber').value = data.numero;
            document.getElementById('roomType').value = data.id_tipo;
            document.getElementById('roomStatus').value = data.estado;
            roomModal.show();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    };

    // 3. Enviar formulario (Crear/Editar)
    roomForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = roomIdInput.value;
        const url = id ? `/habitaciones/editar/${id}` : '/habitaciones/crear';
        const formData = new FormData(roomForm);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.ok) {
                roomModal.hide();
                alert(result.message);
                window.location.reload();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            alert('Error de conexión con el servidor.');
        }
    });

    // 4. Eliminar habitación
    window.deleteRoom = async (id) => {
        if (!confirm('¿Estás seguro de que quieres eliminar esta habitación? Esta acción no se puede deshacer.')) return;

        try {
            const response = await fetch(`/habitaciones/eliminar/${id}`, {
                method: 'POST'
            });
            const result = await response.json();

            if (result.ok) {
                alert(result.message);
                window.location.reload();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            alert('Error de conexión con el servidor.');
        }
    };
});