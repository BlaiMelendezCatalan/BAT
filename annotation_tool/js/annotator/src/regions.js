function setCurrentRegion(id) {
  changePopup = false;
  if (currentRegionId != id){
    changePopup = true;
  }
  currentRegionId = id;
  $('tag').removeClass('active');
  if (currentRegionId != -1) {
    $('.region-label-' + currentRegionId).addClass('active');
    var region = handler.findRegionById(currentRegionId);
    if (region) {
      redrawTagsForRegion(region);
      redrawClassForRegion(region);
      updateRegionIndexes(region);
    }
    if (changePopup) {
      var classes = typeof region.attributes.class != 'undefined' ? region.attributes.class.split(' ') : [];
      if (REGIONS_STATE) {
        toggleProminencePopup(classes, region, $(region.element).offset());
      }
    }
  }
}

function deleteTagFromRegion(region, tagName) {
  if (typeof region.attributes.tags != 'undefined') {
    var position = region.attributes.tags.indexOf(tagName);
    if (position != -1) {
      region.attributes.tags.splice(position, 1);
      updateEvent(region);
      redrawTagsForRegion(region);
    }
  }
}

function redrawClassForRegion(region) {
  $('.class-btn').removeClass('active');
  if (typeof region != 'undefined' && region != null && 'class' in region.attributes) {
    region.attributes['class'].split(' ').forEach(function (name) {
      if (name != '') {
        $('div[data-class-name=' + name + ']').addClass('active');
      }
    });
  }
}

function redrawTagsForRegion(region) {
  var container = $('#tags-container');
  container.empty();
  $('#tags-input').val('');

  if (typeof region != 'undefined' && region != null && 'tags' in region.attributes && typeof region.attributes.tags != 'undefined') {
    region.attributes['tags'].forEach(function (name) {
      if (!name.length) {
        return;
      }
      var deleteTagButton = $('<i></i>')
              .addClass('fa fa-times-circle delete-tag-button')
              .attr('data-tag-name', name);

      var tag = $('<div></div>')
              .addClass('tag-element')
              .text(name);

      deleteTagButton.on('click', function () {
        deleteTagFromRegion(region, $(this).data('tag-name'))
      });

      tag.append(deleteTagButton);
      container.append(tag);
    });
  }
}

function updateRegionIndexes(region) {
  var baseZIndex = 100;
  $('.wavesurfer-region').each(function () {
    $(this).css('z-index', baseZIndex++);
  });
  $('region[data-id=' + region.id + ']').css('z-index', 300);
}

function avoidPaddingOnRegionUpdateEnd(region) {
  if (region.start > handler.getWavesurfer().getDuration() - getPadding()) {
    handler.removeRegion(region, false);
    return false;
  } else if (region.end > handler.getWavesurfer().getDuration() - getPadding()) {
    region.update({
      end: handler.getWavesurfer().getDuration() - getPadding()
    });
  }
  if (region.end < getPadding()) {
    handler.removeRegion(region, false);
    return false;
  } else if (region.start < getPadding()) {
    region.update({
      start: getPadding()
    });
  }

  return true;
}

function adjustRegionLimits(region) {
  var new_start = region.start;
  var new_end = region.end;
  allRegions = handler.getAllRegions();
  min_distance = {};
  min_distance['start'] = [handler.getWavesurfer().getDuration() + 1, new_start];
  min_distance['end'] = [handler.getWavesurfer().getDuration() + 1, new_end];
  allRegions.forEach(function (tmp_region) {
    if (region != tmp_region) {
      if (Math.abs(region.start - tmp_region.start) < min_distance['start'][0]){
        min_distance['start'] = [Math.abs(region.start - tmp_region.start),
                                 tmp_region.start];
      }
      if (Math.abs(region.start - tmp_region.end) < min_distance['start'][0]) {
        min_distance['start'] = [Math.abs(region.start - tmp_region.end),
                                 tmp_region.end];
      }
      if (Math.abs(region.end - tmp_region.start) < min_distance['end'][0]){
        min_distance['end'] = [Math.abs(region.end - tmp_region.start),
                               tmp_region.start];
      }
      if (Math.abs(region.end - tmp_region.end) < min_distance['end'][0]) {
        min_distance['end'] = [Math.abs(region.end - tmp_region.end),
                               tmp_region.end];
      }
    }
  });
  if (min_distance['start'][0] < getPadding() / 10.) {
    new_start = min_distance['start'][1];
    region.update({
      start: new_start
    });
  }
  if (min_distance['end'][0] < getPadding() / 10.) {
    new_end = min_distance['end'][1];
    region.update({
      end: new_end
    });
  }
}

function preventRegionOverlaps(region) {
  var new_start = region.start,
      new_end = region.end,
      wavesurfer = handler.getWavesurfer();
  if (new_end > handler.getWavesurfer().getDuration()) {
    new_end = handler.getWavesurfer().getDuration()
  }
  number_of_partial_overlaps = 0;
  for (var id in wavesurfer.regions.list) {
    if (id == region.id) {
      continue;
    }
    var temp_region = wavesurfer.regions.list[id]
        //offset = $(temp_region.element)[0].offsetLeft;

    if (region.start <= temp_region.end && region.end >= temp_region.start) {
      overlap = true;
      if (region.start >= temp_region.start && region.end <= temp_region.end) {
        handler.removeRegion(region, false);
        return false;
      } else if (region.start <= temp_region.start && region.end >= temp_region.end) {
        handler.removeRegion(region, false);
        return false;
      } else if (region.start <= temp_region.start && region.end <= temp_region.end) {
        number_of_partial_overlaps += 1;
        new_end = temp_region.start;
      } else if (region.start >= temp_region.start && region.end >= temp_region.end) {
        number_of_partial_overlaps += 1;
        new_start = temp_region.end;
      }
    }
  };
  if (number_of_partial_overlaps >= 2) {
    handler.removeRegion(region, false);
    return false;
  }
  region.update({
    start: new_start,
    end: new_end
  });
  return true;
}