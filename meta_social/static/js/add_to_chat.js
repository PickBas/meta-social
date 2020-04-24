function addToChat(e, link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: csr_token,
        },
        success: function () {
            e.target.parentNode.remove();
        }
    })
}