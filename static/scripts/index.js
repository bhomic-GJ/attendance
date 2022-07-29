function fromUTCDate(datestr) {
    const date = new Date(datestr);
    return `${date.getFullYear()}-`+
        `${(date.getMonth()+1).toString().padStart(2, '0')}-`+
        `${date.getDate().toString().padStart(2, '0')}`;
}
function fromUTCTime(timestr) {
    const date = new Date((new Date()).toISOString().split('T')[0] + 'T' + timestr);
    return `${date.getHours()}:${date.getMinutes()}`;
}
function toUTCDate(datestr) {
    if(!datestr) return datestr;
    const date = new Date(datestr + ' ' + (new Date()).toTimeString());
    return date.toISOString();
}
function toUTCTime(timestr) {
    if(!timestr) return timestr;
    const date = new Date((new Date()).toDateString() + ' ' + timestr);
    return date.toISOString().split('T')[1];
}

document.addEventListener('DOMContentLoaded', () => {

    // Get all "navbar-burger" elements
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    // Add a click event on each of them
    $navbarBurgers.forEach(el => {
        el.addEventListener('click', () => {

            // Get the target from the "data-target" attribute
            const target = el.dataset.target;
            const $target = document.getElementById(target);

            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            el.classList.toggle('is-active');
            $target.classList.toggle('is-active');

        });
    });

    (document.querySelectorAll("input[type=time]") || []).forEach(input => {
        if(input.dataset.value)
            input.value = fromUTCTime(input.dataset.value);
        let hidden_field = document.createElement('input');
        hidden_field.type='hidden';
        hidden_field.name = input.dataset.name;
        hidden_field.value = toUTCTime(input.value);
        input.form.appendChild(hidden_field);
        input.addEventListener('input', () => { hidden_field.value = toUTCTime(input.value); });
    });
    (document.querySelectorAll("input[type=date]") || []).forEach(input => {
        if(input.dataset.hasOwnProperty('setMin')) {
            input.min = fromUTCDate((new Date()).toISOString());
            input.value = input.min;
        }if(input.dataset.hasOwnProperty('setCurrent')) {
            input.value = fromUTCDate((new Date()).toISOString());
        }
        if(input.dataset.value)
            input.value = fromUTCDate(input.dataset.value);
        let hidden_field = document.createElement('input');
        hidden_field.type='hidden';
        hidden_field.name = input.dataset.name;
        hidden_field.value = toUTCDate(input.value);
        input.form.appendChild(hidden_field);
        input.addEventListener('input', () => { hidden_field.value = toUTCDate(input.value); });
    });
});