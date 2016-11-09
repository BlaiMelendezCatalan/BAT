function openSegmentResultsInNewWindow(url)
{ 
  var filterParams = document.getElementById('filterParams');
  
  if (filterParams.elements['load_audio'].checked) {
    ParamsStr = "load_audio=checked";
  } else {
    ParamsStr = "load_audio=";
  }
  
  var filters = ['tag', 'tag_filter', 'classified_as', 'groundtruth', 'skew_to_speech'];
  for (var i = 0; i < filters.length; i++) {
    ParamsStr += "&" + filters[i] + "=" + filterParams.elements[filters[i]].value;
  }
  
  if (filterParams.elements['viterbi'].checked) {
    ParamsStr += "&viterbi=checked";
  } else {
    ParamsStr += "&viterbi=";
  }

  window.open(url + "?" + ParamsStr, "_blank");
}


function change_groundtruth(url){
    var new_gt = $(event.target).val();
    $.ajax({  
      url: url,
      type: 'GET',
      data: {'class_value': new_gt},
        success: function(response) {
            console.log(response);
        }
    });
}

function change_optional_groundtruth(url){
    var new_opt_gt = $(event.target).val();
    $.ajax({
      url: url,
      type: 'GET',
      data: {'optional_class_value': new_opt_gt},
        success: function(response) {
            console.log(response);
        }
    });
}

function change_mixed(url){
    var new_mixed = $(event.target).prop('checked');
    $.ajax({
      url: url,
      type: 'GET',
      data: {'mixed': new_mixed},
        success: function(response) {
            console.log(response);
        }
    });
}

function change_commercial(url){
    var new_commercial = $(event.target).prop('checked');
    $.ajax({
      url: url,
      type: 'GET',
      data: {'commercial': new_commercial},
        success: function(response) {
            console.log(response);
        }
    });
}

function change_comments(url){
    var comments = $(event.target).val();
    $.ajax({
      url: url,
      type: 'GET',
      data: {'comments': comments},
        success: function(response) {
            console.log(response);
        }
    });
}


function toggle_tag(url, tag) {
    var cur_val = $(event.target).text();
    if (cur_val == 'add') {
      $(event.target).toggleClass('btn-info btn-danger');
      $(event.target).text('remove');
      $.ajax({
        url: url,
        type: 'GET',
        data: {tag_remove: tag},
          success: function(response) {
            console.log(response);
          }
      });
    }
    else if (cur_val == 'remove') {
      $(event.target).toggleClass('btn-danger btn-info');
      $(event.target).text('add');
      $.ajax({
        url: url,
        type: 'GET',
        data: {tag_add: tag},
          success: function(response) {
            console.log(response);
          }
      });
    }
}


function load_audio_and_peaks(wave, audiourl, peaksurl) {
    $.ajax({
      url: peaksurl,
      success: function (data) {
        wave.load(audiourl, data['peaks']);
        wave.fireEvent("user-action");
      },
      error: function () {
        alert("Error while loading the audio");
      },
      dataType: "json"});
}


function audioFetch(audio_path)
{
    var player = document.getElementById("audio");
    var speed = document.getElementById("speed");
    player.pause();
    player.src = audio_path;
    player.playbackRate = speed.value;
    console.log(player.src);
    player.play();
}

function preloadAudio(url) {
    var audio = new Audio();
    audio.src = url;
    console.log(audio.src);
}
