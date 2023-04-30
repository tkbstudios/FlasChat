document.addEventListener('DOMContentLoaded', () => {
    console.log("from JS: " + username);

    const messagesContainer = document.querySelector('.messages');
    const contentInput = document.getElementById("content");
    const sendMessageForm = document.querySelector("sendMessageForm");
    const sendButton = document.getElementById("sendButton");

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        socket.emit('join');
    });

    contentInput.addEventListener("keypress", function(event) {
    // If the user presses the "Enter" key on the keyboard
    if (event.key === "Enter" && !event.shiftKey) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        sendButton.click();
    }
    });

    contentInput.addEventListener("input", function() {
        // Replace all occurrences of newline character ("\n") with actual newline character
        this.value = this.value.replace(/\n/g, "\r\n");
        });

        socket.on('receive_message', data => {
        console.log('Raw data:', data); // Add this line to log the raw data
        msg_content = data.content.replace(/\n/g, "<br>"); // replace all \n with <br>

        msg_username = data.username;

        messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `<div class="message-username">` + msg_username + `</div><div>` + msg_content + `</div>`;
        document.querySelector('.messages').appendChild(messageElement);
        const messagesContainer = document.querySelector('.messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });

    document.querySelector('form').addEventListener('submit', event => {
        event.preventDefault();
        contentInput.value = contentInput.value.replace(/\n/g, "\r\n");
        const content = document.querySelector('#content').value;
        socket.emit('send_message', {username: username, content: content});
        document.querySelector('#content').value = '';
    });
});