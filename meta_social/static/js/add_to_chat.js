function addToChat(e, link, newUserName, editorId) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: csr_token,
        },
        success: function () {
            chatSocket.send(JSON.stringify({
                'message': 'Был добавлен ' + newUserName + '!',
                'author': editorId,
                'chat_id': roomName,
            }));
            let to_add = e.target.parentNode.parentNode.parentNode;
            if (to_add.tagName === 'DIV') {
                to_add.remove();
            } else {
                to_add = e.target.parentNode.parentNode;
                to_add.remove();
            }
            const amount_to_invite = jQuery('ul#friend-list-modal').children('div').length;
            console.log(amount_to_invite);
            if (amount_to_invite == 0) {
                $('#AddToConvModal').modal('hide');
            }
        }
    })
}
