
document.addEventListener('DOMContentLoaded', () => {


    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


    socket.on('connect', () => {

        input.addEventListener("keyup", function (event) {
            // Number 13 is the "Enter" key on the keyboard
            if (event.keyCode === 13) {
                // Trigger the button element with a click
                document.querySelector('#chat').click();
            };
        });

        document.querySelector('#chat').onclick = () => {
            input = document.querySelector('#input').value;
            if (input.length > 0) {    
                socket.emit('submit chat', {'message': input});
                document.querySelector('#input').value = "";
                return false;
            };
        };
    });

    socket.on('chat added', data => {
        var p = document.createElement('p');
        p.innerHTML = `${data.username}: ${data.chat}`;
        console.log(p);
        document.querySelector('#result').append(p);
    });
  

});
 