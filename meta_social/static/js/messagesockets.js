$(function() {
    autosize(document.getElementById('chat-message-input'));
    document.querySelector('#chat-message-input').focus();
})

let scrolled_by_user = false

ws_connection = 'wss://'

if (window.location.protocol == 'http:') {
    ws_connection = 'ws://'
}

console.log(window.location.protocol)

const chatSocket = new WebSocket(
    ws_connection
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
    if (/\S/.test(message)) {
        let form_data = new FormData($('#message_images')[0])
        
        $.ajax({
            type: 'POST',
            url: '/chat/go_to_chat/' + roomName + '/send_files/',
            data: form_data,
            cache: false,
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

//-------------------------------

function removeMusic(e) {
    let div = document.createElement('div')

    let btn = document.createElement('button')
    btn.classList.add('btn')
    btn.classList.add('btn-sm')
    btn.classList.add('btn-primary')
    btn.innerHTML = '+'
    btn.onclick = function () {
        addMusic(event, $(e.target).attr('music-id'), $(e.target).attr('music-name'))
    }

    let span = document.createElement('span')
    span.classList.add('text-truncate')
    $(span).attr('width', '400px')
    span.innerHTML = $(e.target).attr('music-name')

    div.appendChild(btn)
    div.appendChild(span)

    $('#select-music-list')[0].appendChild(div)
    
    let vals = $('#id_music')[0].value.split(' ')
    for (let i=0; i < vals.length; i++) {
        if (vals[i] == $(e.target).attr('music-id')) {
            vals.splice(i, 1)
        }
    }

    let new_val = ''
    for (let i=0; i < vals.length; i++) {
        new_val += vals[i]
    }

    $('#id_music').val(new_val)

    e.target.parentNode.remove()
}

function getMusicCount() {
    return $('#id_music')[0].value.split(' ').length
}

function addMusic(e, id, name) {
    if (getMusicCount() == 10) {
        alert('Максимум 10 песен')
        return
    }

    $('#id_music')[0].value += id + ' '

    let imgDiv = document.createElement('div')
    imgDiv.classList.add('img-div')
    imgDiv.classList.add('border')

    let nameP = document.createElement('p')
    nameP.classList.add('text-truncate')
    nameP.innerHTML = name

    let rmBtn = document.createElement('span')
    rmBtn.classList.add('message-image-badge');
    rmBtn.classList.add('text-center');
    rmBtn.onclick = removeMusic;
    rmBtn.innerHTML = 'X';
    $(rmBtn).attr('music-name', name)
    $(rmBtn).attr('music-id', id)

    imgDiv.appendChild(nameP)
    imgDiv.appendChild(rmBtn)

    document.getElementById('gallery').appendChild(imgDiv)

    e.target.parentNode.remove()
}

function triggerInput() {
    $('#fileElem')[0].click()
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

    handleFiles(files)
}

function handleFiles(files) {
    files = [...files];
    files.forEach(uploadFile)
}

function get_free_inputs() {
    let inputs = [];
    for (var i = 0; i < 10; i++) {
        let input = document.getElementById("id_form-" + i + "-image");
        if (!input.value) {
            inputs.push(input)
        }
    }
    return inputs
}

function uploadFile(file) {
    let inputs = get_free_inputs();
    
    if (inputs.length == 0) {
        alert('Нельзя загрузить более 10 картинок');
        return
    }

    const dT = new DataTransfer();
    dT.items.add(file);
    inputs[0].files = dT.files;

    let input_id = inputs[0].id[8];

    previewFile(file, input_id)
}

function removeFile(e) {
    let current_id = e.target.id[e.target.id.length - 1];

    document.getElementById("id_form-" + current_id + "-image").value = '';
    e.target.parentNode.remove()
}

function previewFile(file, input_id) {
    let reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function () {
        let imgDiv = document.createElement('div')
        imgDiv.classList.add('img-div')

        let img = document.createElement('img');
        img.src = reader.result;

        let rmBtn = document.createElement('span')

        rmBtn.id = "image_preview-" + input_id;
        rmBtn.classList.add('message-image-badge');
        rmBtn.classList.add('text-center');
        rmBtn.onclick = removeFile;
        rmBtn.innerHTML = 'X';

        imgDiv.appendChild(img)
        imgDiv.appendChild(rmBtn)

        document.getElementById('gallery').appendChild(imgDiv)
    }
}

//--------------------------------------------

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
