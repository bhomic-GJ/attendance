let start_date, end_date, calendar;

function closeAllModals() {
    (document.querySelectorAll('.modal') || []).forEach($modal => {
        $modal.classList.remove('is-active');
    });
}

function reloadPage(start_date) {
    let url = new URL(window.location.href);
    url.searchParams.set(
        "start_date", `${start_date.getFullYear()}-` +
        `${(start_date.getMonth()+1).toString().padStart(2, '0')}-` +
        `${start_date.getDate().toString().padStart(2, '0')}`
    );
    window.location.href = url.href;
}

document.addEventListener('DOMContentLoaded', function () {
    const calendar_element = document.getElementById('calendar');
    const modal            = document.getElementById('modal-js-example');

    calendar = new FullCalendar.Calendar(calendar_element, {
        initialView: 'timeGridWeek',
        initialDate: globalInitDate,
        allDaySlot: false,
        firstDay: 1,
        customButtons: {
            prevPage: {
                text: "Previous",
                icon: 'chevron-left',
                click: () => { reloadPage(start_date); }
            },
            nextPage: {
                text: "Next",
                icon: 'chevron-right',
                click: () => { reloadPage(end_date); }
            },
            addEvent: {
                text: 'Add',
                click: () => { modal.classList.add('is-active'); }
            }
        },
        headerToolbar: {
            right: 'prevPage,nextPage,addEvent'
        },
        viewDidMount: function (view, _) {
            start_date = new Date(Date.parse(view.view.currentStart));
            start_date.setDate(start_date.getDate() - 7);
            end_date = new Date(Date.parse(view.view.currentEnd));
        },
        events: globalEvents,
        eventClick: info => {
            let group = info.event.title.split(' . ')[0].split(' - ')[1];
            let [ start_date, start_time ] = new Date(info.event.startStr).toISOString().split('T', 2);
            let payload = {
                group, start_date, start_time,
                end_time: new Date(info.event.endStr).toISOString().split('T')[1]
            };

            let form = document.createElement('form');
            form.style.visibility = 'hidden';
            form.method = 'POST';
            form.action = globalScheduleRoute;

            for(let key of Object.getOwnPropertyNames(payload)) {
                let input = document.createElement('input');
                input.name = key; input.value = payload[key];
                form.appendChild(input);
            }

            document.body.appendChild(form);
            form.submit();
        }
    });

    calendar.render();

    const today = new Date();
    today.setHours(0); today.setMinutes(0); today.setSeconds(0);
    calendar.scrollToTime(Date.now() - today.getTime() - 3_600_000);

    const $closingElements = (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || [])
    $closingElements.forEach(($close) => {
        const $target = $close.closest('.modal');
        $close.addEventListener('click', () => { $target.classList.remove('is-active'); });
    });

    document.addEventListener('keydown', (event) => {
        const e = event || window.event;
        if (e.key === "Escape") { closeAllModals(); }
    });
});