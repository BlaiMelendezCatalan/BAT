function updateClassProminence(region_id, className, prominence, token) {
  prom_dict = {
    'region_id': region_id,
    'class_name': className,
    'prominence': prominence
  }
  $.ajax({
    type: "POST",
    url: '../update_class_prominence/',
    dataType: 'json',
    data: {
      prom_dict: JSON.stringify(prom_dict),
      csrfmiddlewaretoken: token
    },
  });
}

function closeProminencePopup() {
  var popup = $('#class-prominence-container')
  popup.removeClass('active');
}

function toggleProminencePopup(classes, region, offset) {
  var popup = $('#class-prominence-container');
  if (classes.length == 1) {
    popup.removeClass('active');
    return;
  }
  var offsetLeft1 = offset.left;
  var offsetLeft2 = offset.left - popup.width() + region.element.clientWidth;
  classes.sort()

  // open popup
  if (region.start <= handler.getWavesurfer().getDuration() / 2.) {
    popup.css({
      'top': (offset.top + WAVESURFER_HEIGHT) + 'px',
      'left': offsetLeft1 + 'px'
    });
    popup.addClass('active');
  } else {
    popup.css({
      'top': (offset.top + WAVESURFER_HEIGHT) + 'px',
      'left': offsetLeft2 + 'px'
    });
    popup.addClass('active');
  }

  // remove old classes
  popup.find('.class-prominence-item').not('.fake-item').remove();

  // add current classes
  var fakeItem = popup.find('.fake-item');
  for (var i in classes) {
    var newItem = fakeItem.clone(),
        className = classes[i];
    newItem.removeClass('fake-item');
    newItem.find('.prominence-label').text(className);
    var initProminence = region.attributes.classProminences[className];
    newItem.find('.circle[data-id=' + initProminence + ']').addClass('active');
    popup.append(newItem);

    // click on circle to set prominence
    $(newItem).find('.circle').on('click', function () {
      var className = $(this).closest('.class-prominence-item').find('.prominence-label').text(),
          prominence = $(this).data('id');
      prominences = []
      for (var j in classes) {
        if (classes[j] == className) {
          prominences.push(prominence)
        }
        else {
          prominences.push(region.attributes.classProminences[classes[j]])
        }
      }
      if (prominences.includes(5) || prominences.includes(0)) {
        updateClassProminence(region.attributes.region_id, className, prominence, '{{csrf_token}}');
        region.attributes.classProminences[className] = prominence;

        // mark circle as active
        $(this).closest('.prominence-circles').find('.circle').removeClass('active');
        $(this).addClass('active');
      }
    });
  }

  // activate tooltips
  $('[data-toggle="tooltip"]').tooltip();
}

function checkClassProminenceIsFilled() {
  if (!REGIONS_STATE) {
    return true;
  }
  var wavesurfer = handler.getWavesurfer();
  for (var i in wavesurfer.regions.list) {
    var region = wavesurfer.regions.list[i],
        region_classes = region.attributes.class.split(' ');
    // only regions with multi classes
    if (region_classes.length < 2) {
      continue;
    }
    for (var j in region_classes) {
      var className = region_classes[j];
      if (region.attributes.classProminences[className] == '0') {
        return false;
      }
    }
  }
  return true;
}