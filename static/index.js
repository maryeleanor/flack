
document.addEventListener('DOMContentLoaded', () => {
    
    let room = localStorage.getItem('room');  
    let username = localStorage.getItem('username');
    let image_file = localStorage.getItem('image_file');
    let messageBody = document.querySelector('#chatroom');
   
    // Connect to websocket
    let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

        // on connect, send message to server 
        socket.on('connect', () => {
            if (!room){
                room = 'Home';
            };
            socket.emit('connect to room', {'msg': ' has joined ', 'username': username, 'room': room, 'image_file': image_file});
        });

        // listen for send message from server and append to chatroom
        socket.on('message', data => {  
            console.log(data.username);
            console.log(localStorage.getItem("username"));
            console.log(data.room);
            let current_room;
            if (!data.room){
                current_room = localStorage.getItem('room');
            } else {
                current_room = data.room;
            }
            
            if (data.messages && data.username == localStorage.getItem('username')) {
                console.log(data.messages);
                console.log(data.username);
                console.log(username);
                messages = data.messages;
                if (messages.length > 1) {      
                    messages.forEach(message => { 
                        if (message.chat) { 
                            let span_date = document.createElement('span');
                            span_date.classList.add("date");
                            let img = document.createElement('img');
                            img.classList.add('chatimg');
                            img.alt = "Users profile image";
                            img.src = message.image_file;
                            let span_username = document.createElement('span');
                            span_username.classList.add("username");
                            let p = document.createElement('p');
                            let chat_space = ": ";
                            span_date.innerHTML = message.timestamp;
                            span_username.innerHTML = message.username;
                            p.innerHTML = span_date.outerHTML  + img.outerHTML + span_username.outerHTML + chat_space + message.chat;
                            messageBody.append(p);
                            messageBody.scrollTop = messageBody.scrollHeight;
                        };
                    });
                }; 
            };
            if (messageBody) {
                let span_date = document.createElement('span');
                span_date.classList.add("date");
                let img = document.createElement('img');
                img.classList.add('chatimg');
                img.alt = "Users profile image";
                img.src = data.image_file;
                let span_username = document.createElement('span');
                span_username.classList.add("username");
                let p = document.createElement('p');
                let chat_space = ": ";
                span_date.innerHTML = data.timestamp;
                span_username.innerHTML = data.username;
            
                if (data.msg) {    
                    p.classList.add("sysmessage");
                    p.innerHTML = span_date.outerHTML + img.outerHTML + span_username.outerHTML + data.msg + current_room;
                }
                else if (data.chat) {
                    p.innerHTML = span_date.outerHTML  + img.outerHTML + span_username.outerHTML + chat_space + data.chat;
                }
                else {
                    p.classList.add("sysmessage");
                    p.innerHTML = span_date.outerHTML + img.outerHTML + span_username.outerHTML + data.sysmsg + current_room;
                }
                messageBody.append(p);
                messageBody.scrollTop = messageBody.scrollHeight;
            };
        });

        // when chat send button clicked
        let chat_button = document.querySelector('#send_chat');
        if (chat_button) {
            chat_button.onclick = () => {
            chat = document.querySelector('#chat').value;
            room = localStorage.getItem('room');  
            if (chat.length > 0) {    
                socket.emit('send chat', {'chat': chat, 'room': room, 'image_file': image_file});
                document.querySelector('#chat').value = '';
                document.querySelector('#chat').placeholder = ' ...'; 
                return false;
                };
            };
        };
        
        
        // when room button clicked, get room name, leave old and join new
        document.querySelectorAll('.select_room').forEach(li => {
            li.onclick = () =>{ 
                let newRoom = li.innerHTML; 
                if (newRoom == room) {
                    msg = `You're already in ${room}`;
                    let p = document.createElement('p');
                    p.classList.add("sysmessage");
                    p.innerHTML = msg;
                    messageBody.append(p);
                    messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight;
                } else {
                    messageBody.innerHTML = '';
                    socket.emit('leave', {'username': username, 'room': room, 'image_file': image_file});
                    socket.emit('join', {'username': username, 'room': newRoom, 'image_file': image_file});
                    localStorage.setItem('room', newRoom); 
                    room = newRoom;
                };
            };
                    
        });

        // when createroom button clicked, get room name and leave old room
        let new_channel_button =  document.querySelector('#createroom');
        if (new_channel_button) {
            new_channel_button.onclick = () => {
                room = localStorage.getItem('room');
                socket.emit('leave', {'username': username, 'room': room, 'image_file': image_file}); 
            };
        };
    

});
 