$(function() {
    autosize(document.getElementById('chat-message-input'));
    document.querySelector('#chat-message-input').focus();
})

let scrolled_by_user = false
const chatSocket = new WebSocket(
    'wss://'
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
                setTimeout(scrollChatToBottom, 2000)
            }
        })
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    if (message.length) {
        let form_data = new FormData();
        form_data.append('csrfmiddlewaretoken', c_token);
        
        for (let i=0; i<$('#message_files')[0].files.length; i++) {
            form_data.append('images', $('#message_files')[0].files[i])
        }
        
        $.ajax({
            type: 'POST',
            url: '/chat/go_to_chat/' + roomName + '/send_files/',
            data: form_data,
            contentType: false,
            processData: false,
            success: function (result) {
                let message_id = result;
                
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'author': user_id,
                    'chat_id': roomName,
                    'message_id': message_id, 
                }));
                
                $('#message_files').val('')
                $('#gallery').empty()
            }
        })
        
        messageInputDom.value = '';
    }
};

function triggerInput() {
    $('#message_files')[0].click()
    $('#gallery').empty()
}

let dropArea = document.getElementById('drop-area')

;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation()
}

;['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
})

;['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
});

function highlight(e) {
    dropArea.classList.add('highlight')
}

function unhighlight(e) {
    dropArea.classList.remove('highlight')
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    let dt = e.dataTransfer;
    let files = dt.files;
    
    $('#gallery').empty()
    $('#message_files')[0].files = files
    
    handleFiles($('#message_files')[0])
}

$('#message_files').on('change', function (e) {
    let my_input = e.target
    
    handleFiles(my_input)
})

function handleFiles(my_input) {
    if (my_input.files.length > 10) {
        alert('Нельзя загрузить более 10 файлов')
        my_input.value = ''
        return
    }

    for (let i=0; i<my_input.files.length; i++) {
        let reader = new FileReader()
        reader.readAsDataURL(my_input.files[i]);
        reader.onloadend = function () {
            let imgDiv = document.createElement('div')
            imgDiv.style.cssText = 'position: relative;'
            imgDiv.classList.add('img-div')
            
            let img = document.createElement('img');
            img.src = reader.result;
            
            imgDiv.appendChild(img)

            document.getElementById('gallery').appendChild(imgDiv)
        }
    }
}

$('#messages_list').on('scroll', function () {
    if ($(this).scrollTop() > $(this).height()) {
        scrolled_by_user = false
    } else {
        scrolled_by_user = true
    }
})

$('#chat-message-input').on('input paste', function () {
    scrolled_by_user = false
    scrollChatToBottom()
})

function scrollChatToBottom() {
    if (!scrolled_by_user) {
        let messages = document.getElementById('messages_list');
        messages.scrollTop = messages.scrollHeight;
    }
}
