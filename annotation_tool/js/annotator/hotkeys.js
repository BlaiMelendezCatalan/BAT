function preventOverlappingsOnArrow(current_region, inc=0.0) {
  var new_start, new_end;
  if (inc > 0.0) {
    new_start = current_region.start;
    new_end = current_region.end + inc;
    if (new_end > getDuration()) {
      new_end = getDuration()
    }
  } else if (inc < 0.0) {
    new_start = current_region.start + inc;
    if (new_start < 0.0) {
      new_end = 0.0
    }
    new_end = current_region.end
  }
  Object.keys(wavesurfer.regions.list).forEach(function (id) {
    var region = wavesurfer.regions.list[id];
    if (new_start < region.start && new_end > region.start) {
      console.log('WRONG END')
      new_end = region.start
    } else if (new_start < region.end && new_end > region.end) {
      console.log('WRONG START')
      new_start = region.end
    }
  });

  return [new_start, new_end]
}

function sortRegionsByOption(regions, option) {
  var region_list = [];
  Object.keys(regions).forEach(function (id) {
    region_list.push(regions[id]);
  });
  region_list.sort(function (a, b) {
    return a[option] - b[option];
  });

  return region_list
}

// HTML elements callbacks
document.onkeydown = function (e) {
  e.stopPropagation()
  e.preventDefault()
  var region = wavesurfer.regions.list[currentRegionId]
  var key = e.key;
  console.log(e)
  var n_regions = Object.keys(wavesurfer.regions.list).length
  if (!isNaN(parseInt(key)) && parseInt(key) > 0 && parseInt(key) <= n_regions && e.ctrlKey == true) {
    var region_list = sortRegionsByOption(wavesurfer.regions.list, "start")
    region = region_list[parseInt(key) - 1]
    currentRegionId = region.id
    wavesurfer.seekTo(region.start / wavesurfer.getDuration())
  }

  for (var i = 0; i < CLASS_DICT.length; i++) {
    if (CLASS_DICT[i][2] == key && e.ctrlKey == false) {
      region.update({
        attributes: {
          'class': CLASS_DICT[i][0],
          'tags': region.attributes['tags'],
          'event_id': region.attributes['event_id']
        },
        color: CLASS_DICT[i][1]
      })
      updateEvent(region)
      $("#show_class").val(CLASS_DICT[i][0])
    }
  }
  if (key == " ") {
    wavesurfer.playPause()
  } else if (key == "ArrowLeft" && e.ctrlKey == true && e.shiftKey == false) {
    if (ALLOW_OVERLAPS) {
      times = [region.start, region.end]
    } else {
      times = preventOverlappingsOnArrow(region, increment = -1. / 100)
    }
    region.update({
      start: times[0],
    })
    //updateEvent(region)
  } else if (key == "ArrowRight" && e.ctrlKey == true && e.shiftKey == false) {
    region.update({
      start: region.start + 1. / 100,
    })
    //updateEvent(region)
  } else if (key == "ArrowLeft" && e.ctrlKey == true && e.shiftKey == true) {
    region.update({
      end: region.end - 1. / 100,
    })
    //updateEvent(region)
  } else if (key == "ArrowRight" && e.ctrlKey == true && e.shiftKey == true) {
    times = preventOverlappingsOnArrow(region, increment = 1. / 100)
    region.update({
      end: times[1],
    })
    //updateEvent(region)
  } else if (key == 'b') {
    wavesurfer.seekTo(region.start / wavesurfer.getDuration())
  } else if (key == 's') {
    wavesurfer.seekTo(0.0)
  } else if (key == 'f' || key == 'F') {
    region_list = sortRegionsByOption(wavesurfer.regions.list, "start")
    for (var i = 0; i < region_list.length; i++) {
      if (region == region_list[i]) {
        if (i == 0) {
          if (e.shiftKey == false) {
            new_start = 0.0
          }
          if (region_list.length == 1) {
            if (e.ctrlKey == e.shiftKey) {
              new_end = getDuration()
            }
          } else {
            if (e.ctrlKey == e.shiftKey) {
              new_end = region_list[i + 1].start
            }
          }
        } else if (i == region_list.length - 1) {
          if (e.shiftKey == false) {
            new_start = region_list[i - 1].end
          }
          if (e.ctrlKey == e.shiftKey) {
            new_end = getDuration()
          }
        } else {
          if (e.shiftKey == false) {
            new_start = region_list[i - 1].end
          }
          if (e.ctrlKey == e.shiftKey) {
            new_end = region_list[i + 1].start
          }
        }
        region.update({
          start: new_start,
          end: new_end,
        })
        updateEvent(region)
        break;
      }
    }
  }
}


document.onkeyup = function (e) {
  var key = e.key
  if (key == "ArrowLeft" || key == "ArrowRight") {
    Object.keys(wavesurfer.regions.list).forEach(function (id) {
      var region = wavesurfer.regions.list[id];
      updateEvent(region)
    });
  }
}