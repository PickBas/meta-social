function editChatName(e, link) {
    let edited_text = document.getElementById("id-chat-name-change");
    let old_text = document.getElementById("chat_name");
    $.ajax({
        type: "POST",
        url: link,
        data: {
          csrfmiddlewaretoken: csr_token,
          text: edited_text.value
        },
        success: function() {
          old_text.innerText = edited_text.value;
          console.log(old_text)
        }
    })
}