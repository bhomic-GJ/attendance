document.addEventListener('DOMContentLoaded', () => {
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
});