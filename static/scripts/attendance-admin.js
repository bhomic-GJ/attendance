let donutopen = 0;
let donutdiv = document.querySelector('.donutdiv');

const LAUNCH_MESSAGE = String.raw`
Ask your organization members to mark their attendances by logging
in to the website and scanning the QR shown on your screen.

A live count of present and absent people is also shown.

Use the 'Toggle Chart' button to toggle the visibility of the pie.

Note: The QR code is likely to be refreshed upon tab switch, so better to avoid the same.
`;

function toggleDonut() {
    donutopen = (donutopen + 1) % 2;

    if (donutopen == 1) {
        donutdiv.style.transform = "scale(1)";
    } else {
        donutdiv.style.transform = "scale(0)";
    }
}

function populateChart(chart, { present = 0, absent = 0 } = {}) {
    chart.data.datasets[0].data = [ present, absent ];
    chart.update();
}

document.addEventListener('DOMContentLoaded', () => {
    donutdiv = document.querySelector('.donutdiv');
    toggleDonut();
    document.querySelector('.donutopener').addEventListener('click', () => {
        toggleDonut();
    });

    const ctx = document.getElementById("PA_chart").getContext("2d");
    const chart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Present", "Absent"],
            datasets: [{
                backgroundColor: ["#2b5797", "#b91d47"],
                data: [0, 0],
            }]
        },
        options: {
            responsive: true,
            layout: {
                padding: {
                    left: 0,
                    right: 0,
                    top: 0,
                    bottom: 0,
                },
            },
        },
    });

    let socket = io();

    socket.on('connect', () => {
        alert(LAUNCH_MESSAGE);
        socket.emit('SYN', "admin");
        socket.on('respond', data => {
            console.log(data);
        })
        socket.on('SYN-ACK', (info) => {
            console.log(info);
            populateChart(chart, info);
        });
        socket.on('count_update', info => {
            console.log(info);
            populateChart(chart, info);
        });
    });

    window.onunload = () => { socket.disconnect(true); }
});