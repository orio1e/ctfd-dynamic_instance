	CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    //const md = _CTFd.lib.markdown()
    })
    function  tojson(form) {
        var params= Array();
        Object.keys(form).forEach(function(x) {
            if (form[x] === "true") {
                params[x] = true;
            } else if (form[x] === "false") {
                params[x] = false;
            } else {
                params[x] = form[x];
            }
        });
        return params;
    }
    $('#addserver').click(function() {
        
        CTFd.fetch("/plugins/dynamic_instance/new", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                'Accept': "application/json",
                "Content-Type":"multipart/form-data"
              },
            body: JSON.stringify(tojson($('#addserverform').serializeArray()))
        }).then(response => response.json())
        .then(json => CTFd.ui.ezq.ezAlert({
            title: "alert",
            body: json,
            button: "OK"
        }))
        //.then(window.location.reload())
        .catch(err => console.log('Request Failed', err)); 
    });
    $("#createimage").click(function(){
        CTFd.fetch("/plugins/dynamic_instance/new", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                'Accept': "application/json",
                "Content-Type":"application/json"
              },
            body: JSON.stringify(tojson($('#createimageform').serializeArray()))
        }).then(response => response.json())
        .then(json => CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: json,
            button: "OK"
        }))
        //.then(window.location.reload())
        .catch(err => console.log('Request Failed', err)); 
    });
    $("#setconfig").click(function(){
        CTFd.fetch("/plugins/dynamic_instance/config", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                'Accept': "application/json",
                "Content-Type":"application/json"
              },
            body: JSON.stringify(tojson($('#configform').serializeArray()))
        }).then(response => response.json())
        .then(json => CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: json,
            button: "OK"
        }))
        //.then(window.location.reload())
        .catch(err => console.log('Request Failed', err)); 
    });
function delete_server(server_id) {
        CTFd.fetch("/plugins/dynamic_instance/delserver/"+server_id, {
            method: "DELETE",
            credentials: "same-origin",
            headers: {
                'Accept': "application/json",
                "Content-Type":"application/json"
              },
        }).then(response => response.json())
        .then(json => CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: json,
            button: "OK"
        }))
        .catch(err => console.log('Request Failed', err)); 
    
   
}
function delete_image(image_id) {
    CTFd.fetch("/plugins/dynamic_instance/delimage/"+image_id, {
        method: "DELETE",
        credentials: "same-origin",
        headers: {
            'Accept': "application/json",
            "Content-Type":"application/json"
          },
    }).then(response => response.json())
    .then(json => CTFd.ui.ezq.ezAlert({
        title: "INFO",
        body: json,
        button: "OK"
    }))
    .catch(err => console.log('Request Failed', err)); 



}

    
	
