
document.addEventListener('DOMContentLoaded', () => {
    
    let room = localStorage.getItem('room');  
    let username = localStorage.getItem('username');
    // console.log(username)
    // console.log(room)

    // scroll chatroom to bottom in case there's a lot of messages
    var messageBody = document.querySelector('#chatroom');
    messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight;

    // trigger chat button click with enter key 
    input = document.querySelector('#chat');  
    input.addEventListener("keyup", event => {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) { 
            document.querySelector('#send_chat').click();
        };
    });


    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

        // on connect, send message to server
        socket.on('connect', () => {
            room = localStorage.getItem('room');
            socket.emit('connect to room', {'msg': ' has joined ', 'room': room});
        });

        // listen for send message from server and append to chatroom
        socket.on('message', data => {  
            if (data.messages) {
                messages = data.messages;
                if (messages.length > 1) {     
                    console.log(messages)
                    messages.forEach(message => { 
                        if (message.chat) { 
                            var span_date = document.createElement('span');
                            span_date.classList.add("date");
                            var span_username = document.createElement('span');
                            span_username.classList.add("username");
                            var p = document.createElement('p');
                            var chat_space = ": ";
                            span_date.innerHTML = message.timestamp;
                            span_username.innerHTML = message.username;
                            p.innerHTML = span_date.outerHTML  + span_username.outerHTML + chat_space + message.chat;
                            messageBody.append(p);
                            messageBody.scrollTop = messageBody.scrollHeight;
                        };
                    });
                    }; 
                };

            var span_date = document.createElement('span');
            span_date.classList.add("date");
            var span_username = document.createElement('span');
            span_username.classList.add("username");
            var p = document.createElement('p');
            var chat_space = ": ";
            span_date.innerHTML = data.timestamp;
            span_username.innerHTML = data.username;
        
            if (data.msg) {    
                p.classList.add("sysmessage");
                p.innerHTML = span_date.outerHTML  + span_username.outerHTML + data.msg + data.room;
            }
            else if (data.chat) {
                p.innerHTML = span_date.outerHTML  + span_username.outerHTML + chat_space + data.chat;
            }
            else {
                p.classList.add("sysmessage");
                p.innerHTML = span_date.outerHTML  + span_username.outerHTML + data.sysmsg + data.room;;
            }
            messageBody.append(p);
            messageBody.scrollTop = messageBody.scrollHeight;
        });

        // when chat send button clicked
        document.querySelector('#send_chat').onclick = () => {
            chat = document.querySelector('#chat').value;
            room = localStorage.getItem('room');  
            if (chat.length > 0) {    
                socket.emit('send chat', {'chat': chat, 'room': room});
                document.querySelector('#chat').value = '';
                document.querySelector('#chat').placeholder = ' ...'; 
                return false;
            };
        };
        
        // when room button clicked, get room name, leave old and join new
        document.querySelectorAll('.select_room').forEach(li => {
            li.onclick = () =>{ 
                let newRoom = li.innerHTML; 
                if (newRoom == room) {
                    msg = `You're already in ${room}`;
                    var p = document.createElement('p');
                    p.classList.add("sysmessage");
                    p.innerHTML = msg;
                    messageBody.append(p);
                } else {
                    messageBody.innerHTML = '';
                    socket.emit('leave', {'username': username, 'room': room});
                    socket.emit('join', {'username': username, 'room': newRoom});
                    localStorage.setItem('room', newRoom); 
                    room = newRoom;
                }
            }
                    
        });



         // when createroom button clicked, get room name, leave old and join new
        document.querySelector('#createroom').onclick = () => {
                room = localStorage.getItem('room');
                socket.emit('leave', {'username': username, 'room': room}); 
            }
        



});
 