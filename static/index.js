document.addEventListener('DOMContentLoaded', () => {
    console.log("from JS: " + username);
    const socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', () => {
        socket.emit('join');
    });

    socket.on('receive_message', data => {
        console.log('Raw data:', data); // Add this line to log the raw data
        msg_content = data.content;
        msg_username = data.username;

        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `<div class="message-username">` + msg_username + `</div><div>` + msg_content + `</div>`;
        document.querySelector('.messages').appendChild(messageElement);
//        const messagesContainer = document.querySelector('.messages');
//        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });




    document.querySelector('form').addEventListener('submit', event => {
        event.preventDefault();
        const content = document.querySelector('#content').value;
        socket.emit('send_message', {username: username, content: content});
        document.querySelector('#content').value = '';
    });
});