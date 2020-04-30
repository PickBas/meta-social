autosize(document.getElementById('chat-message-input'));


const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    let text_area = document.getElementById('chat-message-input');
    $.ajax({
            type: "POST",
            url: '/chat/go_to_chat/' + roomName + '/get_messages/',
            data: {
                csrfmiddlewaretoken: c_token,
                text: text_area.value,
            },
            success: function (result) {
                document.getElementById('messages_list').innerHTML = result;
            }
        })
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    if (message.length) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'author': user_id,
            'chat_id': roomName,
        }));
        messageInputDom.value = '';
    }
};
