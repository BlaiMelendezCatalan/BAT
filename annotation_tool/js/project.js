$(function () {
  // delete items with ajax DELETE request
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

  // autocomplete for tag field
  if (typeof TAGS_NAMES != 'undefined') {
    $('#tokenfield').tokenfield({
      autocomplete: {
        source: TAGS_NAMES,
        delay: 100
      },
      showAutocompleteOnFocus: true
    })
  }

  // open modal when page was opened
  if (typeof OPEN_MODAL != 'undefined' && OPEN_MODAL) {
    $('#add-item-button').trigger('click');
  }

  // color picker init
  var color_input = $('#color-picker');
  if (color_input.length) {
    color_input.colorpicker({'format': 'hex'});
  }
});