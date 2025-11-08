var pc = null;
var socket;
var host = window.location.hostname;

function showMessage(message) {
        console.log(message);
    }

var server="ws://"+host+":8765";
function negotiate() {
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    return pc.createOffer().then((offer) => {
        return pc.setLocalDescription(offer);
    }).then(() => {
        // wait for ICE gathering to complete
        return new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                const checkState = () => {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(() => {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then((response) => {
        return response.json();
    }).then((answer) => {
        return pc.setRemoteDescription(answer);
    }).catch((e) => {
        alert(e);
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

//    if (document.getElementById('use-stun').checked) {
//        config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
//    }

    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', (evt) => {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate();
    document.getElementById('stop').style.display = 'inline-block';
	        if (socket === undefined || socket.readyState !== 1) {
            socket = new WebSocket(server);
        } else {
            showMessage('Надо закрыть уже имеющееся соединение');
        }

        /*
         * четыре функции обратного вызова: одна при получении данных и три – при изменениях в состоянии соединения
         */
        socket.onmessage = function (event) { // при получении данных от сервера
            //showMessage(event.data);
			var socketObject=JSON.parse(event.data);
			let table=document.getElementById('recognition-result');
			if (socketObject.defined==false)
				var def='<span style="color:red;">False</span>';
			else
				var def='<span style="color:green;">True</span>';
			table.innerHTML+=`<tr><td><img style="width:100px;" src="data:image/jpeg;base64, ${socketObject.image}"</td><td>${def}</td><td>${socketObject.label}</td></tr>`;
        }
        socket.onopen = function () { // при установке соединения с сервером
            showMessage('Соединение с сервером установлено');
        }
        socket.onerror = function(error) { // если произошла какая-то ошибка
            showMessage('Произошла ошибка: ' + error.message);
        };
        socket.onclose = function(event) { // при закрытии соединения с сервером
            showMessage('Соединение с сервером закрыто');
            if (event.wasClean) {
                showMessage('Соединение закрыто чисто');
            } else {
                showMessage('Обрыв соединения'); // например, «убит» процесс сервера
            }
            showMessage('Код: ' + event.code + ', причина: ' + event.reason);
        };
}

function stop() {
    document.getElementById('stop').style.display = 'none';
	document.getElementById('start').style.display = 'inline-block';
	    document.getElementById('disconnect').onclick = function () {
        if (socket !== undefined && socket.readyState === 1) {
            socket.close();
        } else {
            showMessage('Соединение с сервером уже было закрыто');
        }
    };
    // close peer connection
    setTimeout(() => {
        pc.close();
    }, 500);
}
