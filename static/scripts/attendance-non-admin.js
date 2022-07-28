import QrScanner from "./qr-scanner.min.js";

let form;
const FAILURE_MESSAGE = String.raw`
There was an error while scanning the QR.
Ensure that a valid QR generated for one of your organization's schedule is being scanned.
`

const qrScanner = new QrScanner(
    document.getElementById("videoElement"),
    result => {
        qrScanner.stop();
        console.log('decoded qr code:', result);
        try {
            let data = JSON.parse(result.data);
            if(data.Token) {
                for(const property of Object.getOwnPropertyNames(data)) {
                    form[property].value = data[property];
                }
                form.submit();
            }
            // fetchData("/api/schedule/attend", {
            //     method: 'POST',
            //     body: { ...data },
            //     credentials: 'same-origin'
            // })
            // .then(response => {
            //     console.log(response);
            //     if (!response.status)
            //         throw new Error(`HTTP ${response.code}: ${response.error}`);
            //     // redirect
            //     window.location.href = "/";
            // })
            // .catch(reason => {
            //     console.error(reason);
            //     qrScanner.start();
            // })

        } catch (error) {
            alert(FAILURE_MESSAGE);
            alert(error);
            qrScanner.start();
        }
    }, {}
);

QrScanner.listCameras(true).then(devices => {
    for (var i = 0; i < devices.length; i++) {
        var device = devices[i];
        var option = document.createElement('option');
        option.value = device.id;
        option.text = device.label || 'camera ' + (i + 1);
        document.querySelector('select#videoSource').appendChild(option);
    }
}) // async; requesting camera labels, potentially asking the user for permission

document.addEventListener('DOMContentLoaded', () => {
    form = document.getElementById("detailsForm");
});

document.querySelector('select#videoSource').onchange = e => {
    qrScanner.setCamera(e.target.value);
}

let qrtoggle = 0;
document.querySelector('#qrbtn').addEventListener('click', () => {
    qrtoggle = (qrtoggle + 1) % 2;
    if (qrtoggle == 1) {
        qrScanner.start();
    } else {
        qrScanner.stop();
    }
});

window.onunload = () => {
    qrScanner.destroy();
}