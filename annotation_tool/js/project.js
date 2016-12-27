$(function () {
  $('.delete-item').on('click', function () {
    var url = $(this).data('delete-url');
    $('#delete-url').val(url);
  });
  $('#delete-button').on('click', function () {
    $.ajax({
      url: $('#delete-url').val(),
      beforeSend: function(xhr) {
          xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
      },
      type: 'DELETE',
      success: function () {
        //reset page
        location.reload()
      }
    });
  });
});