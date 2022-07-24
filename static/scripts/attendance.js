async function fetchData (url, options = {})
{
    try {
        if(options) {
            if(options.method == "POST" && typeof options.body == "object") {
                let bodydata = new FormData();
                for(const property of Object.getOwnPropertyNames(options.body))
                    bodydata.append(property, options.body[property]);
                options.body = bodydata;
            }
        }
        let response = await fetch(url, options);
        console.log(response.status);
        let data = await response.json();
        return data;
    }
    catch(reason) {
        console.error(reason);
    }
}
