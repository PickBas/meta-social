function msNavButtonsInit() {
    $('.ms-nav-btn').addClass('btn btn-outline-primary waves-effect mx-0 w-100 px-0 py-2 text-left')
    $('.ms-nav-btn-active').addClass('btn btn-primary waves-effect mx-0 w-100 px-0 py-2 text-left')
}

$(document).ready(function () {
    $('.badge-right').click(function () {
        if (event.offsetX > this.offsetWidth - 36) {
            event.preventDefault()
            
            window.location.href = $(event.target).attr('second-href')
        }
    })

    msNavButtonsInit()
})