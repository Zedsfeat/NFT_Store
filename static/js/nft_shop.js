function checkDeleteAdvert(id) {
    let text = "Are you sure you want to delete the advert?"
    if (confirm(text)) {
        window.location.replace('/advert/' + id + '/delete')
    }
}

function checkDeleteProfile() {
    let text = 'Are you sure you want to delete the profile?'
    if (confirm(text)) {
        window.location.replace('/profile/delete')
    }
}

// Бустраповское модальное окно
$('#myModal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
})