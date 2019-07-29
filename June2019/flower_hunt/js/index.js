var pre_question_arr = ['flower', 'fruit', 'leaf']; //Pre questions to be asked
var pre_q_index = 0; //To track which preliminary question to ask
var attr_group_obj; //The json of attribute groups
//Some vars for the main data table
var attr_header = null,
  data_rows = null,
  map_rows = null; //Map to convert back to textual values

var skip_col_arr = []; //The array with skiped col ids
var used_val_arr = []; //The array with used values
var decisson_state_index = 0; //The global index to track access the array with data for pre and next questions

window.onload = init();
function init() {
  // Load files into variables
  var file_array = ['data/attribute_group.json', 'data/d_flower_data_mapped.tsv', 'data/value_map1.tsv'];
  for (file_path of file_array) {
    loadDoc(file_path);
  }

  get_media();
  ask_init_question(-1);
}

//Add ending result of species to the container
function add_species_info_boxes(species_name_arr) {
  for (species_name of species_name_arr) {
    var info_box = document.createElement('div');
    info_box.className = 'info_box';

    info_box.innerHTML =
      '<img src="image/flower/' +
      species_name +
      '.jpg" />' +
      '<div><p>' +
      species_name +
      '</p>' +
      '<label onclick="go_wiki(\'' +
      species_name.split(' ').join('_') +
      '\')">More Details</label>' +
      '</div>';

    document.getElementById('info_box_container').appendChild(info_box);
  }
}

// Ask user preliminary questions to get the attributes that will be used
function ask_init_question(anwser) {
  var q_container = document.getElementById('question');
  q_container.innerHTML = 'Pre-Q: Do you see a ' + pre_question_arr[pre_q_index] + '?';
  display_img('q_img', 'image/question/' + pre_question_arr[pre_q_index] + '.jpg');
  //When anw is fals, change it to null in array
  if (anwser == 0) {
    pre_question_arr[pre_q_index - 1] = null;
  }
  pre_q_index++;
  //When all init questions are asked
  if (pre_q_index == 4) {
    var q_groupe_num = 0;
    for (q_group of pre_question_arr) {
      if (q_group != null) {
        q_groupe_num++;
      }
    }

    // When too little features are observed
    if (q_groupe_num < 2) {
      pre_q_index = 0;
      pre_question_arr = ['flower', 'fruit', 'leaf'];

      // Display alert
      swal({
        title: 'Try again',
        text:
          'To obtain an accurate result, \
          please make sure the plant has at two of the following features: flower, fruit, and leaf.',
        icon: 'warning',
        button: 'Ok'
      });

      //Ask the pre qustions again
      ask_init_question(-1);
    } else {
      q_container.innerHTML =
        'Now loading...<br>It might take a while to get your first question (less than a minute).';
      document.getElementById('yes_button').style.display = 'none';
      document.getElementById('no_button').style.display = 'none';
      display_img('q_img', 'image/icon/loading.gif');
      //When at leat on group of attributes is missing, remove them from table
      if (q_groupe_num == 2) {
        skip_col_arr = get_skip_cols(pre_question_arr);
      }

      // Interactive decisson tree startss
      setTimeout(function() {
        //Start with the top hirachy (order)
        find_best_questions(3);
      }, 1000);

      document.getElementById('yes_button').setAttribute('onclick', "ask_question('1')");
      document.getElementById('no_button').setAttribute('onclick', "ask_question('0')");
    }
  }
}

//Remove the questions not accesed from the object
function update_obj() {
  var cur_q_index = decision_arrays[decisson_state_index][3];
  var cur_q_objs = decision_arrays[decisson_state_index][2];

  var new_obj = {};

  for (var i = 0; i < cur_q_index + 1; i++) {
    new_obj[Object.keys(cur_q_objs)[i]] = cur_q_objs[Object.keys(cur_q_objs)[i]];
  }

  decision_arrays[decisson_state_index][2] = new_obj;
}

//Update the skip col ids according to the anwser to the current question
function updete_skip_col(method) {
  var cur_q_objs = decision_arrays[decisson_state_index][2];
  var cur_q_index = decision_arrays[decisson_state_index][3];
  var skip_col_id = cur_q_objs[Object.keys(cur_q_objs)[cur_q_index]][0];
  if (method == 'add') skip_col_arr.push(skip_col_id);
  else skip_col_arr.remove(skip_col_id);
}

function display_img(id, url, url_2 = '') {
  var img = document.getElementById(id);
  img.src = url;
  img.style.display = 'block';

  img.onerror = function(e) {
    document.getElementById(id).src = url_2;
    img.onerror = function(e2) {
      document.getElementById(id).style.display = 'none';
    };
  };
}

//Display the current question
function put_question() {
  var cur_q_objs = decision_arrays[decisson_state_index][2];
  if (!cur_q_objs || cur_q_objs.length == 0) return -1;
  var cur_q_index = decision_arrays[decisson_state_index][3];
  var col_val_pair = cur_q_objs[Object.keys(cur_q_objs)[cur_q_index]];
  var cur_attribute = attr_header[col_val_pair[0]].toLowerCase();

  var question;
  var img_val_name = '';

  //If the current value to ask is numeric, then ask directly
  if (NUMERIC_COL_IDS.includes(col_val_pair[0])) {
    question = 'Is ' + cur_attribute + ': ' + col_val_pair[1];
    img_val_name = col_val_pair[1];
  }
  //If the cur val is categorical, then restore it using map before asking
  else {
    var q_prefix = '';
    var q_end = '';
    if (map_rows[col_val_pair[1]][2] != undefined) {
      q_prefix = map_rows[col_val_pair[1]][2] + ' ';
    }

    if (map_rows[col_val_pair[1]][1] != undefined && map_rows[col_val_pair[1]][1] != '') {
      q_end = ': ' + map_rows[col_val_pair[1]][1];
      img_val_name = map_rows[col_val_pair[1]][1];
    }
    question = q_prefix + cur_attribute + q_end;
  }

  display_img(
    'q_img',
    'image/question/' + cur_attribute + '-' + img_val_name + '.png',
    'image/question/' + cur_attribute + '.png'
  );
  document.getElementById('question').innerHTML = question + '?';
}

//Display the pure label at a level
function display_results() {
  for (var class_num = 0; class_num < 4; class_num++) {
    var level_set = uniquecounts(data_rows, class_num);
    //When one of the levels become pure
    if (Object.keys(level_set).length == 1) {
      document.getElementById('hiera_' + String(class_num)).innerHTML = Object.keys(level_set)[0];
      document.getElementById('hiera_' + String(class_num)).style.opacity = '1.0';
      if (class_num == 0) {
        end_game();
      }
    } else {
      document.getElementById('hiera_' + String(class_num)).style.opacity = '0.3';
      document.getElementById('hiera_' + String(class_num)).innerHTML = '???';
    }
  }
}

//End the question and display results
function end_game() {
  //Remove the old info boxes
  removeElementsByClass('info_box');
  //Add the new ones
  add_species_info_boxes(Object.keys(uniquecounts(data_rows, 0)));
  change_state('result');
}

//Make dicision to continue spliting based on the user's anwser, or end game and show results
var last_anw = null;
function make_decision(anwser) {
  last_anw = anwser;
  //Point global data rows to current rows
  data_rows = decision_arrays[decisson_state_index][0];
  var new_col_id = get_new_class_id(0.0001);
  //Get the true set of rows
  var new_rows = get_new_rows(anwser);

  //If no valid rows to split based on the anwser, end the game
  if (new_col_id == null || new_rows.length == 0) {
    end_game();
  } else {
    display_results();

    //Split as we can
    if (Object.keys(uniquecounts(data_rows, 0)).length > 1) {
      //Now point the global rows to the true set of rows
      data_rows = new_rows;
      setTimeout(function() {
        find_best_questions(new_col_id);
      }, 500);
    }
  }
}

function ask_question(anwser) {
  //Called by find_best_questions function to show the best question
  if (anwser == -1) {
    decisson_state_index = decision_arrays.length - 1;
    var q_exists = put_question();

    //When no questions can be asked, end the game
    if (q_exists == -1) {
      end_game();
    } else {
      document.getElementById('yes_button').style.display = 'block';
      document.getElementById('no_button').style.display = 'block';
      document.getElementById('q_next').style.display = 'flex';
      //If no next question
      if (Object.keys(decision_arrays[decisson_state_index][2]).length < 2) {
        document.getElementById('q_next').setAttribute('onclick', 'end_game()');
        document.getElementById('q_next').innerHTML = 'End';
      }

      //When there is at least one pre q
      if (decisson_state_index != 0) document.getElementById('q_pre').style.display = 'flex';
    }
  }

  //True anwser
  else if (anwser == 1) {
    document.getElementById('yes_button').style.display = 'none';
    document.getElementById('no_button').style.display = 'none';
    document.getElementById('q_pre').style.display = 'none';
    document.getElementById('q_next').style.display = 'none';
    document.getElementById('question').innerHTML = 'Now loading...';
    display_img('q_img', 'image/icon/loading.gif');
    update_obj();

    make_decision(0);
  }

  //False answer
  else if (anwser == 0) {
    document.getElementById('yes_button').style.display = 'none';
    document.getElementById('no_button').style.display = 'none';
    document.getElementById('q_pre').style.display = 'none';
    document.getElementById('q_next').style.display = 'none';
    document.getElementById('question').innerHTML = 'Now loading...';
    display_img('q_img', 'image/icon/loading.gif');
    update_obj();

    make_decision(1);
  }

  //Skip question
  else if (anwser == 'next') {
    document.getElementById('q_pre').style.display = 'flex';
    updete_skip_col('add');

    //Raise the index of current state question by one
    if (decision_arrays[decisson_state_index][3] < Object.keys(decision_arrays[decisson_state_index][2]).length - 1) {
      decision_arrays[decisson_state_index][3]++;
    }
    //Othwerwise, try to go to next set of decision array if any
    else if (decisson_state_index < decision_arrays.length - 1) {
      decisson_state_index += 1;
    }

    //If no next questions
    if (
      decision_arrays[decisson_state_index][3] >= Object.keys(decision_arrays[decisson_state_index][2]).length - 1 &&
      decisson_state_index >= decision_arrays.length - 1
    ) {
      document.getElementById('q_next').setAttribute('onclick', 'end_game()');
      document.getElementById('q_next').innerHTML = 'End';
    }

    put_question();
  }

  //Go to previous question
  else {
    document.getElementById('q_next').setAttribute('onclick', "ask_question('next')");
    document.getElementById('q_next').innerHTML = '>';

    //Decrease the index of current state question by one
    if (decision_arrays[decisson_state_index][3] > 0) {
      decision_arrays[decisson_state_index][3]--;
    }
    //Othwerwise, try to go to previous set of decision array if any
    else if (decisson_state_index > 0) {
      decisson_state_index -= 1;
    }

    updete_skip_col('remove');
    //If no precious questions
    if (decision_arrays[decisson_state_index][3] == 0 && decisson_state_index == 0) {
      document.getElementById('q_pre').style.display = 'none';
    }

    put_question();
  }
}

function removeElementsByClass(className) {
  var elements = document.getElementsByClassName(className);
  while (elements.length > 0) {
    elements[0].parentNode.removeChild(elements[0]);
  }
}

function go_wiki(img_url) {
  window.open('https://en.wikipedia.org/wiki/' + img_url);
}

//To swich b/w frames
function change_state(state) {
  // change to the chooseInput frame
  if (state == 'input') {
    document.querySelector('main').className = 'ChooseInputFrame';
    location.reload();
  }
  //change to takePic frame
  if (state == 'video') {
    document.querySelector('main').className = 'TakePicFrame';
    document.getElementById('logo_container').style.display = 'none';
    document.getElementById('input_button_container').style.display = 'none';
    document.getElementById('video_container').style.display = 'flex';

    document.getElementById('question_container').style.display = 'none';
    document.getElementById('result_container').style.display = 'none';
  }
  //change to question frame
  if (state == 'question') {
    document.querySelector('main').className = 'QuestionFrame';
    document.getElementById('logo_container').style.display = 'none';
    document.getElementById('input_button_container').style.display = 'none';
    document.getElementById('video_container').style.display = 'none';

    document.getElementById('result_container').style.display = 'none';
    document.getElementById('question_container').style.display = 'flex';
  }
  //change to result frame
  if (state == 'result') {
    document.getElementById('yes_button').style.display = 'block';
    document.getElementById('no_button').style.display = 'block';
    document.getElementById('q_pre').style.display = 'flex';
    document.getElementById('q_next').style.display = 'flex';
    put_question();

    document.querySelector('main').className = 'ResultFrame';
    document.getElementById('input_button_container').style.display = 'none';

    document.getElementById('question_container').style.display = 'none';
    document.getElementById('result_container').style.display = 'flex';
  }
}
