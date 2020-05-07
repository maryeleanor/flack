
document.addEventListener('DOMContentLoaded', () => {

    var messageBody = document.querySelector('#home_room');
    messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight;

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', () => {

        input = document.querySelector('#chat');  

        input.addEventListener("keyup", function (event) {
            // Number 13 is the "Enter" key on the keyboard
            if (event.keyCode === 13) {
                // Trigger the button element with a click
                document.querySelector('#send_chat').click();
            };
        });

        document.querySelector('#send_chat').onclick = () => {
            chat = document.querySelector('#chat').value;
            if (chat.length > 0) {    
                socket.emit('submit chat', {'message': chat});
                document.querySelector('#chat').value = "";
                return false;
            };
        };
   

        socket.on('chat added', data => {
            var p = document.createElement('p');
            p.innerHTML = `${data.chat}`;
            console.log(p);
            document.querySelector('#home_room').append(p);
            messageBody.scrollTop = messageBody.scrollHeight; 
            if (!localStorage.getItem('home')) {
                localStorage.setItem('home', data.home);    
            };
        });
        

        document.querySelector('#room2').onclick = () => {
        socket.emit('create', 'room2');

            // server side code
            io.sockets.on('connection', function(socket) {
            socket.on('create', function(room2) {
                socket.join(room2);
                    });
            });
            
        };
        
    });

});
 