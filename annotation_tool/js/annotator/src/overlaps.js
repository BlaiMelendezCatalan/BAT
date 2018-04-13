function switchToRegionMode() {
  REGIONS_STATE = true;
  $('#solve-overlaps-button, region .fa-times-circle, #tag_button, region handle, #add-wavesurfer-button, #tags-input-tokenfield, .tags-input-container, .only-pre-solve-overlaps').hide();
  $('.class-btn').css('cursor', 'default');
  $('#back-annotations-button, #regions-mode-tag-label').show();
  handler.disableDragSelection();
}

function switchToEventMode() {
  REGIONS_STATE = false;
  $('#solve-overlaps-button, region .fa-times-circle, #tag_button, region handle, #add-wavesurfer-button, #tags-input-tokenfield, .tags-input-container, .only-pre-solve-overlaps').show();
  $('.class-btn').css('cursor', 'pointer');
  $('#back-annotations-button, #regions-mode-tag-label').hide();
  closeProminencePopup();
  handler.enableDragSelection();
}

function checkOverlaps() {
  wavesurfer = handler.getWavesurfer();
  if (REGIONS_STATE || !('regions' in wavesurfer)) {
    return false;
  }
  var overlapWasFound = false,
      regionList = wavesurfer.regions.list
  for (var i in regionList) {
    if (overlapWasFound) { break; }
    var region = regionList[i];
    for (var j in regionList) {
      var tmp_region = regionList[j];
      if (region != tmp_region) {
        if (region.start <= tmp_region.end && region.end >= tmp_region.start) {
          if (!(region.end == tmp_region.start && region.start < tmp_region.start) && !(region.start == tmp_region.end && region.end > tmp_region.end)) {
            overlapWasFound = true;
            break;
          }
        }
      }
    }
  }
  $('#solve-overlaps-button').attr('disabled', !overlapWasFound);
  return overlapWasFound;
}

function solveOverlaps(allRegions) {
  var newRegions = {};
  if (typeof allRegions == 'object') {
    allRegions = $.map(allRegions, function (item) {
      return item;
    });
  }

  var region_borders = [];
  allRegions.forEach(function (region) {
    if (typeof region.deleted != 'undefined') {
      return;
    }
    if (!region_borders.includes(region.start)) {
      region_borders.push(region.start)
    }
    if (!region_borders.includes(region.end)) {
      region_borders.push(region.end)
    }
  });

  region_borders.sort(function(a, b){
    return a - b;
  });

  for (var i = 0; i < region_borders.length - 1; i++) {
    var createRegion = false;
    var classes = []
    var tags = []
    var color = 'rgba(0, 0, 0, 0.5)'
    allRegions.forEach(function (region) {
      if (region_borders[i] >= region.start && region_borders[i + 1] <= region.end) {
        classes.push(region.attributes.class)
        var region_tags = typeof region.attributes.tags != 'undefined' ? region.attributes.tags : [];
        tags = tags.concat(region_tags)
        color = sumColor(color, region.color)
        createRegion = true
      }
    });
    if (createRegion) {
      newRegions[i] = {}
      newRegions[i]['classes'] = getUniqueItems(classes)
      newRegions[i]['tags'] = getUniqueItems(tags)
      newRegions[i]['start'] = region_borders[i]
      newRegions[i]['end'] = region_borders[i + 1]
      newRegions[i]['color'] = color;
    }
  }

  allRegions.forEach(function (region) {
    handler.removeRegion(region, false);
  });

  for (var i in newRegions) {
    if (newRegions[i]['start'] != newRegions[i]['end']) {
      var newRegion = handler.addRegion(
        handler.getWavesurfer(),
        'region',
        newRegions[i]['classes'].sort().join(' '),
        newRegions[i]['tags'],
        -1,
        newRegions[i]['start'],
        newRegions[i]['end'],
        newRegions[i]['color'],
        true
      );
    }
  }
  handler.rearrangeLabels();
}

function clearRegionsOnBack() {
  var regionList = this.wavesurfer.regions.list
  for (var i in regionList) {
    handler.removeRegion(regionList[i], true)
  }
}

function loadEventsOnBack(event_dict) {
  for (var i in event_dict) {
    handler.addRegion(
      handler.getWavesurfer(),
      'event',
      event_dict[i]['event_class'],
      event_dict[i]['tags'],
      event_dict[i]['event_id'],
      event_dict[i]['start_time'],
      event_dict[i]['end_time'],
      event_dict[i]['color'],
      false
    );
  }
}

function backToAnnotation(back_data, token) {
  $.ajax({
    type: "POST",
    url: '../remove_regions/',
    dataType: 'json',
    data: {
      back_data: JSON.stringify(back_data),
      csrfmiddlewaretoken: token
    },
    success: function (event_dict) {
      clearRegionsOnBack();
      loadEventsOnBack(event_dict);
      switchToEventMode();
      handler.rearrangeLabels();
      checkOverlaps();
    }
  });
}

function sumColor(color, current_color) {
  if (color == current_color) {
    return color;
  }
  var rgba = color.split('(')[1]
  rgba = rgba.substring(0, rgba.length - 1)
  var [r, g, b, a] = rgba.split(', ')
  var current_rgba = current_color.split('(')[1]
  current_rgba = current_rgba.substring(0, current_rgba.length - 1)
  var [cr, cg, cb, ca] = current_rgba.split(', ')
  rr = parseInt(r) + parseInt(cr)
  rg = parseInt(g) + parseInt(cg)
  rb = parseInt(b) + parseInt(cb)
  max = Math.max(rr, rg, rb)
  if (rr == rg && rg == rb) {
    rg = 0;
    rb = rb / 1.5;
    rr = rr * 1.5;
  }
  if (max > 0) {
    rr = rr / max * 255.;
    rg = rg / max * 255.;
    rb = rb / max * 255.;
  }
  result_color = 'rgba(' + rr.toString() + ', ' + rg.toString() + ', ' + rb.toString() + ', ' + a.toString() + ')'
  return result_color;
}