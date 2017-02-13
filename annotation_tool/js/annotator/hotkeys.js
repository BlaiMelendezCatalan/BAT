function preventOverlapsOnArrow(current_region, inc=0.0) {
  var new_start, new_end,
    current_id = current_region.id;

  if (inc > 0.0) {
    new_start = current_region.start;
    new_end = current_region.end + inc;
    if (new_end > getTotalDuration()) {
      new_end = getTotalDuration()
    }
  } else if (inc < 0.0) {
    new_start = current_region.start + inc;
    if (new_start < 0.0) {
      new_end = 0.0
    }
    new_end = current_region.end
  }
  if (!ALLOW_OVERLAPS) {
    var wavesurfer = handler.getMainWavesurfer();
    Object.keys(wavesurfer.regions.list).forEach(function (id) {
      if (current_id == id) {
        return;
      }
      var region = wavesurfer.regions.list[id];
      if (new_start < region.start && new_end > region.start) {
        new_end = region.start
      } else if (new_start < region.end && new_end > region.end) {
        new_start = region.end
      }
    });
  }

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

// glue the selected region limits to the closer borders
function glueSelectedRegionLimits(region, pressCtrl, pressShift, overlaps) {
  var wavesurfer = handler.getMainWavesurfer(),
    region_list = sortRegionsByOption(wavesurfer.regions.list, "start"),
    new_start, new_end;
  if (!overlaps) {
    for (var i = 0; i < region_list.length; i++) {
      if (region == region_list[i]) {
        if (i == 0) {
          if (!pressShift) {
            new_start = 0.0
          }
          if (region_list.length == 1) {
            if (pressCtrl == pressShift) {
              new_end = getTotalDuration()
            }
          } else {
            if (pressCtrl == pressShift) {
              new_end = region_list[i + 1].start
            }
          }
        } else if (i == region_list.length - 1) {
          if (!pressShift) {
            new_start = region_list[i - 1].end
          }
          if (pressShift == pressCtrl) {
            new_end = getTotalDuration()
          }
        } else {
          if (!pressShift) {
            new_start = region_list[i - 1].end
          }
          if (pressShift == pressCtrl) {
            new_end = region_list[i + 1].start
          }
        }
        region.update({
          start: new_start,
          end: new_end
        });
        updateEvent(region);
        break;
      }
    }
  } else {
    for (var i = 0; i < region_list.length; i++) {
      if (region == region_list[i]) {
        if (!pressShift) {
          new_start = 0.0
        }
        if (pressCtrl == pressShift) {
          new_end = getTotalDuration()
        }
        region.update({
          start: new_start,
          end: new_end
        });
        updateEvent(region);
        break;
      }
    }
  }
  insertLog(
      "shortcut F",
      getTime(),
      pressCtrl.toString() + ' ' + pressShift.toString());
  console.log("shortcut F")
}

function setClassForRegion(region, class_name, color) {
  region.update({
    attributes: {
      'class': class_name,
      'tags': region.attributes['tags'],
      'event_id': region.attributes['event_id']
    },
    color: color,
    annotation: class_name
  });
  updateEvent(region);
  redrawClassForRegion(region);
  insertLog("update region class", getTime(), class_name)
  console.log("update region class")
}

function getTotalDuration() {
  return getDuration() - 0.0001
}

// HTML elements callbacks
document.onkeydown = function (e) {
  if (e.target == $('#tags-input-tokenfield')[0]) {
    return;
  }
  e.stopPropagation();
  e.preventDefault();

  var region = handler.findRegionById(currentRegionId),
    key = e.key,
    wavesurfer = handler.getWavesurferByRegion(region),
    n_regions = wavesurfer ? Object.keys(wavesurfer.regions.list).length : 0,
    pressCtrl = e.ctrlKey == true,
    pressShift = e.shiftKey == true,
    isNotPlayerKey = ' sb'.indexOf(key) == -1,
    times;

  if ((REGIONS_STATE || currentRegionId == -1) && isNotPlayerKey) {
    return;
  }

  // set class for region
  for (var i = 0; i < CLASS_DICT.length; i++) {
    if (CLASS_DICT[i][2] == key && !pressCtrl) {
      setClassForRegion(region, CLASS_DICT[i][0], CLASS_DICT[i][1])
    }
  }

  if (key == " ") {
    handler.playPause();
  } else if (key == "ArrowLeft" && pressCtrl && !pressShift) {
    times = preventOverlapsOnArrow(region, increment = -1. / 100)
    region.update({start: times[0]});
  } else if (key == "ArrowRight" && pressCtrl && !pressShift) {
    region.update({start: region.start + 1. / 100});
  } else if (key == "ArrowLeft" && pressCtrl && pressShift) {
    region.update({end: region.end - 1. / 100});
  } else if (key == "ArrowRight" && pressCtrl && pressShift) {
    times = preventOverlapsOnArrow(region, increment = 1. / 100)
    region.update({end: times[1]});
  } else if (key == 'b' && region != null) {
    handler.seekTo(region.start / getTotalDuration());
    insertLog("shortcut B", getTime());
    console.log("shortcut B")
  } else if (key == 's') {
    handler.seekTo(0.0);
    insertLog("shortcut S", getTime());
    console.log("shortcut S")
  } else if (key == 'f' || key == 'F') {
    glueSelectedRegionLimits(region, pressCtrl, pressShift, ALLOW_OVERLAPS);
  }
  if (ALLOW_OVERLAPS) {
    handler.checkOverlaps();
  }
}


document.onkeyup = function (e) {
  var key = e.key;
  if (key == "ArrowLeft" || key == "ArrowRight") {
    if (currentRegionId != -1) {
      region = wavesurfer.regions.list[currentRegionId];
      updateEvent(region);
      insertLog("update region limits keyboard",
                getTime(),
                region.start.toString() + ' ' + region.end.toString());
      console.log("update region limits keyboard")
    }
  }
}