document.addEventListener('DOMContentLoaded', () => {
    const edit = document.getElementById('edit');
    const save = document.getElementById('save');
    const cancel = document.getElementById('cancel');

    const fields = Array.from(document.getElementById('userform').elements)
        .filter(element => (
            element.classList.contains('is-static') &&
            !element?.datalist?.hasOwnProperty?.('persistent')
        ));

    edit.addEventListener('click', e => {
        e.preventDefault();

        edit.classList.add('is-hidden');
        save.classList.remove('is-hidden');
        cancel.classList.remove('is-hidden');

        fields.forEach(element => {
            element.classList.remove('is-static');
            element.readOnly=false;
        });
    });

    cancel.addEventListener('click', e => {
        edit.classList.remove('is-hidden');
        save.classList.add('is-hidden');
        cancel.classList.add('is-hidden');

        fields.forEach(element => {
            element.classList.add('is-static');
            element.readOnly=true;
        });
    });
});