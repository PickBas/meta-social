function createConversation(e, link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: csr_token,
            text: name.value,
        },
        success: function (result) {
            document.getElementById('chat-list').innerHTML = result;
        }
    })
}