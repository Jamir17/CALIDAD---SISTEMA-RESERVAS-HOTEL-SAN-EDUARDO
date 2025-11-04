// Datos de ejemplo (se mantendrán hasta conectar con el backend)
const sampleData = [
    { id: 1, codigo: 'RES-001', habitacion: '101', entrada: '2024-11-15', salida: '2024-11-18', noches: 3, estado: 'confirmed', monto: 450.00 },
    { id: 2, codigo: 'RES-002', habitacion: '205', entrada: '2024-11-20', salida: '2024-11-25', noches: 5, estado: 'confirmed', monto: 850.00 },
    { id: 3, codigo: 'RES-003', habitacion: '312', entrada: '2024-12-01', salida: '2024-12-03', noches: 2, estado: 'pending', monto: 300.00 },
];

let currentData = [];

function loadData() {
    currentData = [...sampleData];
    updateStats();
    renderTable();
}

function updateStats() {
    const totalReservas = currentData.length;
    const totalNoches = currentData.reduce((sum, r) => sum + r.noches, 0);
    const totalGasto = currentData.reduce((sum, r) => sum + r.monto, 0);
    const ticketPromedio = totalReservas > 0 ? totalGasto / totalReservas : 0;

    document.getElementById('totalReservas').textContent = totalReservas;
    document.getElementById('totalNoches').textContent = totalNoches;
    document.getElementById('totalGasto').textContent = totalGasto.toFixed(2);
    document.getElementById('ticketPromedio').textContent = ticketPromedio.toFixed(2);
}

function renderTable() {
    const tbody = document.querySelector('#reservasTable tbody');
    
    if (currentData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-secondary); padding: 3rem 1rem;">📭 Sin resultados</td></tr>';
        return;
    }

    tbody.innerHTML = currentData.map((r, idx) => `
        <tr>
            <td>${idx + 1}</td>
            <td>${r.codigo}</td>
            <td>${r.habitacion}</td>
            <td>${formatDate(r.entrada)}</td>
            <td>${formatDate(r.salida)}</td>
            <td>${r.noches}</td>
            <td>
                <span class="status-badge status-${r.estado}">
                    ${r.estado === 'confirmed' ? 'Confirmada' : 'Pendiente'}
                </span>
            </td>
            <td>$${r.monto.toFixed(2)}</td>
        </tr>
    `).join('');
}

function applyFilters() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const type = document.getElementById('filterType').value;
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;

    currentData = sampleData.filter(r => {
        const matchSearch = r.codigo.toLowerCase().includes(search) || r.habitacion.includes(search);
        const matchType = !type || r.estado === type;
        const matchDate = (!dateFrom || r.entrada >= dateFrom) && (!dateTo || r.salida <= dateTo);
        
        return matchSearch && matchType && matchDate;
    });

    updateStats();
    renderTable();
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('filterType').value = '';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    
    loadData();
}

function exportCSV() {
    if (currentData.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    let csv = 'Código,Habitación,Entrada,Salida,Noches,Estado,Monto\n';
    csv += currentData.map(r => `${r.codigo},${r.habitacion},${r.entrada},${r.salida},${r.noches},${r.estado},${r.monto}`).join('\n');

    const link = document.createElement('a');
    link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    link.download = 'reservas.csv';
    link.click();
}

function printData() {
    window.print();
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES');
}

// Asignación de eventos
const form = document.getElementById('filterForm');
if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault(); // Evita que el formulario se envíe de la forma tradicional
        applyFilters();
    });
    form.addEventListener('reset', (e) => {
        // Da un pequeño tiempo para que el reset del navegador ocurra antes de recargar los datos
        setTimeout(() => {
            loadData();
        }, 0);
    });
}

const exportCsvBtn = document.getElementById('exportCsvBtn');
if (exportCsvBtn) {
    exportCsvBtn.addEventListener('click', exportCSV);
}

const printBtn = document.getElementById('printBtn');
if (printBtn) {
    printBtn.addEventListener('click', printData);
}

// Carga inicial de datos
loadData();