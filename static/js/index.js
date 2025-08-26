// index.js (tabs)
document.addEventListener('click', (e) => {
  if(!e.target.matches('.tab-button')) return;
  const id = e.target.getAttribute('data-tab');
  document.querySelectorAll('.tab-button').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  e.target.classList.add('active');
  document.getElementById(id).classList.add('active');
});
