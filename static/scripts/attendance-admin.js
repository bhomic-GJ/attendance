/*document.addEventListener('DOMContentLoaded', () => {
    let socket = io();

    socket.emit('SYN', "admin");
    socket.on('SYN-ACK', () => {
        // Init GUI
    });
    socket.on('count_update', info => {
        console.log(info);
    });

    window.onunload = () => { socket.disconnect(true); }
});*/


let donutopen = 0;
let donutdiv = document.querySelector('.donutdiv');

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
    document.querySelector('.donutopener').onclick = function(){
        toggleDonut();
    };

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
    populateChart(chart, { present: 4, absent: 60 });

    // let socket = io();

    // socket.emit('SYN', "admin");
    // socket.on('SYN-ACK', () => {
    //     // Init GUI
    // });
    // socket.on('count_update', info => {
    //     console.log(info);
    //     populateChart(chart, info);
    // });

    // window.onunload = () => { socket.disconnect(true); }
});