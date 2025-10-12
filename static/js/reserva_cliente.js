// Reservas form functionality

// Precios por tipo de habitación
const precios = {
  standard: 120,
  junior: 180,
  presidential: 280
};

// Nombres de habitaciones
const nombresHabitaciones = {
  standard: 'Habitación Standard',
  junior: 'Habitación Junior',
  presidential: 'Suite Presidential'
};

// Set minimum date to today
document.addEventListener('DOMContentLoaded', function() {
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('checkin').setAttribute('min', today);
  document.getElementById('checkout').setAttribute('min', today);

  // Update summary on form changes
  const form = document.getElementById('reservasForm');
  form.addEventListener('input', updateSummary);
  form.addEventListener('change', updateSummary);

  // Prevent selecting checkout date before checkin
  document.getElementById('checkin').addEventListener('change', function() {
    const checkinDate = this.value;
    document.getElementById('checkout').setAttribute('min', checkinDate);
    updateSummary();
  });

  // Form submission
  form.addEventListener('submit', handleSubmit);
});

function updateSummary() {
  const checkin = document.getElementById('checkin').value;
  const checkout = document.getElementById('checkout').value;
  const habitacion = document.getElementById('habitacion').value;
  const huespedes = document.getElementById('huespedes').value;

  // Update dates
  document.getElementById('summaryCheckin').textContent = 
    checkin ? formatDate(checkin) : '--/--/----';
  document.getElementById('summaryCheckout').textContent = 
    checkout ? formatDate(checkout) : '--/--/----';

  // Calculate nights
  let noches = 0;
  if (checkin && checkout) {
    const checkinDate = new Date(checkin);
    const checkoutDate = new Date(checkout);
    const diffTime = checkoutDate - checkinDate;
    noches = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (noches < 0) noches = 0;
  }
  document.getElementById('summaryNoches').textContent = noches;

  // Update room type
  document.getElementById('summaryHabitacion').textContent = 
    habitacion ? nombresHabitaciones[habitacion] : 'No seleccionada';

  // Update guests
  document.getElementById('summaryHuespedes').textContent = 
    huespedes || '0';

  // Calculate total
  let total = 0;
  if (habitacion && noches > 0) {
    total = precios[habitacion] * noches;
  }
  document.getElementById('summaryTotal').textContent = `S/. ${total.toFixed(2)}`;
}

function formatDate(dateString) {
  const date = new Date(dateString + 'T00:00:00');
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

function handleSubmit(e) {
  e.preventDefault();

  // Get form data
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  // Validate dates
  const checkinDate = new Date(data.checkin);
  const checkoutDate = new Date(data.checkout);
  
  if (checkoutDate <= checkinDate) {
    alert('La fecha de salida debe ser posterior a la fecha de llegada.');
    return;
  }

  // Validate terms
  if (!data.terminos) {
    alert('Debe aceptar los términos y condiciones para continuar.');
    return;
  }

  // Calculate nights and total
  const diffTime = checkoutDate - checkinDate;
  const noches = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  const total = precios[data.habitacion] * noches;

  // Prepare reservation data
  const reserva = {
    ...data,
    noches: noches,
    total: total,
    fecha_reserva: new Date().toISOString(),
    estado: 'pendiente'
  };

  // Log reservation (in production, this would be sent to a server)
  console.log('Reserva confirmada:', reserva);

  // Show success message
  alert(`¡Reserva confirmada!\n\nDetalles:\n- Habitación: ${nombresHabitaciones[data.habitacion]}\n- Llegada: ${formatDate(data.checkin)}\n- Salida: ${formatDate(data.checkout)}\n- Noches: ${noches}\n- Total: S/. ${total.toFixed(2)}\n\nRecibirá un correo de confirmación en breve.`);

  // Reset form
  e.target.reset();
  updateSummary();

  // Redirect to home page
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 2000);
}
