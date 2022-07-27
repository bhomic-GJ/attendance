import QrScanner from "./qr-scanner.min.js";

const qrScanner = new QrScanner(
    document.getElementById("videoElement"),
    result => {
        qrScanner.stop();
        console.log('decoded qr code:', result);

        try {

            let data = JSON.parse(result);
            console.log(data);


        } catch (error) {

        }

        // getUserData()
        //     .then(user => fetchData("/api/schedule/mark", {
        //         method: 'POST',
        //         body: { ...data },
        //         credentials: 'same-origin'
        //     }))
        //     .then(response => {
        //         console.log(response);
        //         if (!response.status)
        //             throw new Error(`HTTP ${response.code}: ${response.error}`);
        //         // redirect
        //         window.location.href = "/";
        //     })
        //     .catch(reason => {
        //         console.error(reason);
        //         qrScanner.start();
        //     })
    }, {}
);

//shinchan changed
let qrtoggle = 0;
document.querySelector('#qrbtn').addEventListener('click', () => {
    qrtoggle = (qrtoggle + 1)%2;
    if(qrtoggle == 1){
        qrScanner.start();
    }    
    else{
        qrScanner.stop();
    }
});

window.onunload = () => {
    qrScanner.destroy();
}