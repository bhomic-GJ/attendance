document.addEventListener('DOMContentLoaded', () => {
    let socket = io();

    socket.emit('SYN', "admin");
    socket.on('SYN-ACK', () => {
        // Init GUI
    });
    socket.on('count_update', info => {
        console.log(info);
    });

    window.onunload = () => { socket.disconnect(true); }
});