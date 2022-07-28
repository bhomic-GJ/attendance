document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.switch').forEach(element => {
        element.addEventListener('change', () => {
            element.form.submit();
        });
    });

    document.querySelectorAll('.groupform').forEach(form => {
        const select_div = form.group.closest('div.field');
        const user_ids   = form.user_ids instanceof RadioNodeList ? form.user_ids : [ form.user_ids ];
        user_ids.forEach(radio => radio.addEventListener('change', e => {
            if(Array.from(user_ids).reduce((acc, elm) => acc + (elm.checked ? 1: 0), 0) > 0)
                select_div.classList.remove('is-hidden');
            else select_div.classList.add('is-hidden');
        }));
        form.querySelector('.select_all_members')?.addEventListener('click', e => {
            user_ids.forEach(radio => { radio.checked = true; });
            select_div.classList.remove('is-hidden');
            e.target.checked = false;
        })
    });

    const edit = document.getElementById('edit');
    const save = document.getElementById('save');
    const cancel = document.getElementById('cancel');

    const fields = Array.from(document.getElementById('editForm').elements)
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