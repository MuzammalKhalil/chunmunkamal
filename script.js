const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
menu?.addEventListener('click', () => {
  const expanded = menu.getAttribute('aria-expanded') === 'true';
  menu.setAttribute('aria-expanded', String(!expanded));
  navigation.classList.toggle('open', !expanded);
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
    menu.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
    menu.focus();
  }
});
const form = document.querySelector('#contact-form');
if (form) {
  const programme = new URLSearchParams(location.search).get('programme');
  if (programme && [...form.elements.programme.options].some(option => option.value === programme)) form.elements.programme.value = programme;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const body = `Name: ${data.get('firstName')} ${data.get('lastName')}\nEmail: ${data.get('email')}\nPhone: ${data.get('phone')}\nHeard about you: ${data.get('source')}\nProgramme: ${data.get('programme')}\n\n${data.get('message')}`;
    location.href = `mailto:hello@chunmunkamal.com?subject=${encodeURIComponent('Coaching enquiry: ' + (data.get('programme') || 'General'))}&body=${encodeURIComponent(body)}`;
    document.querySelector('#form-status').textContent = 'Your email app has been requested. Please send the email there. If it does not open, email hello@chunmunkamal.com directly.';
  });
}
