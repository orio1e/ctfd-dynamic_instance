CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd.lib.markdown();


CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown)
}


CTFd._internal.challenge.postRender = function () {info(); }

var askbooting;
var instance_endtime;

function info(){
    var challenge_id = parseInt($('#challenge-id').val());
    var url = "/plugins/dynamic_instance/instanceinfo/" + challenge_id;
    CTFd.fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }   
    }).then(function(response) {
        if (response.status === 429) {
            return response.json();
        }
        if (response.status === 403) {
            return response.json();
        }
        return response.json();
    }).then(function(response) {
        
        if(response.type === "notboot"){
            $('#instance').html(
            '<div class="cardstyle="width: 100%;>'+'<div class="card-body" >' +
            '<h4 class="card-title">Instance Pannel</h4>'+
            '<button type="button" class="btn btn-primary center" id="bootinstance" onclick="boot()">Create instance</button>' +
            '</div></div>');
            if (askbooting !== undefined) {
                clearInterval(askbooting);
                
            }
           
        } else {
            if(response.type === "booting"){
                $('#instance').html('<div style="width: 100%;>'+'<div class="card-body" >' +
                '<h4 class="card-title">Instance Pannel</h4>'+'<h5 class="card-title">booting....</h5>'+
                '</div></div>');
                if (askbooting !== undefined) {
                    clearInterval(askbooting);
                    
                    
                }askbooting=setInterval(info,1000);


        }else{
            if(response.type === "booted"){
                if (askbooting !== undefined) {
                    clearInterval(askbooting);   
                }
                $('#instance').html(
                    '<div class="card" style="width: 100%;>'+'<div class="card-body" >' +
                '<h4 class="card-title">Instance Pannel</h4>'+'<h5 ><a href='+response.host+'>'+response.host+'</a></h5>'+
                '<p>'+echoportmap(response.portmap)+'</p>'+'<h5>RemainTime:</h5><h5 id="clock"></h5>'+
                '<button type="button" class="btn  btn-primary card-link" id="extense" onclick="extense()">Extense time</button><br/>' +
                '<button type="button" class="btn  btn-success card-link" id="reload" onclick="reload()">Reload Instance</button><br/>' +
                '<button type="button" class="btn btn-danger card-link" id="destroy" onclick="destroy()">Destroy Instance</button>' +
                '</div></div>'
                    );
                instance_endtime=response.endtime;
                clock=setInterval(countDown(),1000);
                
            } 

        }
        }
        
    });
}




CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var submission = CTFd.lib.$('#challenge-input').val()

    var body = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    var params = {}
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};

function boot() {
    $('#instance').html('<div class="cardstyle="width: 100%;>'+'<div class="card-body" >' +
    '<h4 class="card-title">Instance Pannel</h4>'+'<h5 class="card-title">booting....</h5>'+
    '</div></div>');
    askbooting=setInterval(info,1000);
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    CTFd.fetch("/plugins/dynamic_instance/bootinstance/"+challenge_id, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }   
    }).then(function(response) {
        if (response.status === 429) {
            return response.json();
        }
        if (response.status === 403) {
            return response.json();
        }
        return response.json();
    }).then(function(response) {
        CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: response,
            button: "OK"
        });
    });
}
function destroy() {
    askbooting=setInterval(info,1000);
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    CTFd.fetch("/plugins/dynamic_instance/destroyinstance/"+challenge_id, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }   
    }).then(function(response) {
        if (response.status === 429) {
            return response.json();
        }
        if (response.status === 403) {
            return response.json();
        }
        return response.json();
    }).then(function(response) {
        CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: response,
            button: "OK"
        });
    });
}
function extense() {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    CTFd.fetch("/plugins/dynamic_instance/exttime/"+challenge_id, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }   
    }).then(function(response) {
        if (response.status === 429) {
            return response.json();
        }
        if (response.status === 403) {
            return response.json();
        }
        return response.json();
    }).then(function(response) {
        CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: response,
            button: "OK"
        });
        info();
    });
}
function reload() {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    CTFd.fetch("/plugins/dynamic_instance/reload/"+challenge_id, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }   
    }).then(function(response) {
        if (response.status === 429) {
            return response.json();
        }
        if (response.status === 403) {
            return response.json();
        }
        return response.json();
    }).then(function(response) {
        CTFd.ui.ezq.ezAlert({
            title: "INFO",
            body: response,
            button: "OK"
        });
    });
}




function echoportmap(portmap) {
    result="Ports bind:";
    for (host in portmap) {
        result+=portmap[host]+' =>'+host+"   ";
    }
    return result
}

function addZero(i) {
    return i < 10 ? "0" + i: i + "";
    }

function countDown() {          
    var nowtime = new Date();
    var endtime = new Date(instance_endtime*1000);
    var lefttime = parseInt((endtime.getTime() - nowtime.getTime())/1000);
    var h = parseInt(lefttime / (60 * 60) % 24);
    var m = parseInt(lefttime / 60 % 60);
    var s = parseInt(lefttime % 60);
    h = addZero(h);
    m = addZero(m);
    s = addZero(s);
    $("#clock").html(`${h}:${m}:${s}`);

    if (lefttime <= 0) {
        $("#clock").html("00:00:00");
        clearInterval(countDown);
        return;
    }
    setTimeout(countDown, 1000);
    }
