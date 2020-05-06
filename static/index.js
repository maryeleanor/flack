
document.addEventListener('DOMContentLoaded', () => {


    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit vote" event
        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {
                const selection = button.dataset.vote;
                socket.emit('submit vote', { 'selection': selection });
            };
        });
    });

    // When a new vote is announced, add to the unordered list
    socket.on('announce vote', data => {
        const li = document.createElement('li');
        console.log(li)
        li.innerHTML = `Vote recorded: ${data.selection}`;
        document.querySelector('#votes').append(li);
    });

    //////

    socket.on('connect', () => {
        document.querySelector('#submit').onclick = () => {
            input = document.querySelector('#input').value;
            socket.emit('submit chat', {'message': input});
        };
    });

    socket.on('chat added', data => {
        var p = document.createElement('p');
        p.innerHTML = `${data.chat}`;
        console.log(p);
        document.querySelector('#result').append(p);
    });
 



});
 