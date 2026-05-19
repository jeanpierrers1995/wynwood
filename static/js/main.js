
document.addEventListener('DOMContentLoaded', () => {
  const checkIn  = document.getElementById('id_check_in');
  const checkOut = document.getElementById('id_check_out');
  if (checkIn && checkOut) {
    checkIn.addEventListener('change', () => {
      checkOut.min = checkIn.value;
      if (checkOut.value && checkOut.value <= checkIn.value) {
        checkOut.value = '';
      }
    });
    const today = new Date().toISOString().split('T')[0];
    checkIn.min  = today;
    checkOut.min = today;
  }

  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity .4s ease';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 400);
    }, 4000);
  });

  document.querySelectorAll('.card-fav').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const icon = btn.querySelector('i');
      if (icon.classList.contains('bi-heart')) {
        icon.classList.replace('bi-heart', 'bi-heart-fill');
        icon.style.color = 'var(--gold)';
      } else {
        icon.classList.replace('bi-heart-fill', 'bi-heart');
        icon.style.color = '';
      }
    });
  });

  const cardNumber = document.querySelector('input[name="card_number"]');
  if (cardNumber) {
    cardNumber.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '').substring(0, 16);
      e.target.value = v.replace(/(.{4})/g, '$1 ').trim();
    });
  }

  const expiry = document.querySelector('input[name="card_expiry"]');
  if (expiry) {
    expiry.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '').substring(0, 4);
      if (v.length >= 2) v = v.slice(0, 2) + '/' + v.slice(2);
      e.target.value = v;
    });
  }

});
