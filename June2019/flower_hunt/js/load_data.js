//Convert the map raw file into an array
function read_map_tsv(file_str) {
  var rows = file_str.split('\n');
  for (var i = 0; i < rows.length; i++) {
    val = rows[i].trim().split('\t');
    rows[i] = val;
  }
  map_rows = rows; //global
}

// Put the header and raw file into the arries from raw file
function process_plant_tsv(file_str) {
  var rows = [];
  var feature_arr = [];
  var row_id = 0;
  var header = true;

  var lines = file_str.split('\n');
  for (line of lines) {
    row_id += 1;
    var arr = line.trim().split('\t');
    //  Get an array of header
    if (header) {
      num_of_cols = arr.length;
      for (var i = 0; i < num_of_cols; i++) {
        feature_arr.push(arr[i].trim());
      }
      header = false;
    } else {
      if (arr.length < num_of_cols) {
        console.log('Error on row', row_id, 'Not enough columns!', arr);
        continue;
      }
      for (var i = 0; i < arr.length; i++) {
        arr[i] = arr[i].trim();
      }

      row = arr.slice(0, num_of_cols);
      labels = arr.slice(num_of_cols, arr.length);
      rows.push([row].concat([labels]));
    }
  }

  attr_header = feature_arr; //global
  data_rows = rows; //global
}

//Remove attributes & values according to user's anwser
function trim_table(user_attr_array) {
  var user_attributes = [];
  for (attr_group of user_attr_array) {
    if (attr_group != null) {
      user_attributes = user_attributes.concat(attr_group_obj[attr_group]);
    }
  }
  user_attributes = user_attributes.concat(attr_group_obj['other']); // add the attributes grouped in other anyway
  var temp_table = [[], []];
  for (var i = 0; i < data_rows.length; i++) {
    temp_table[1].push([[], data_rows[i][1]]);
  }
  for (var col_id = 0; col_id < attr_header.length; col_id++) {
    if (user_attributes.includes(attr_header[col_id])) {
      temp_table[0].push(attr_header[col_id]);
      for (var row_id = 0; row_id < data_rows.length; row_id++) {
        temp_table[1][row_id][0].push(data_rows[row_id][0][col_id]);
      }
    }
  }

  //Now point the global header and rows var to the trimed ones
  attr_header = temp_table[0];
  data_rows = temp_table[1];
  console.log(attr_header, data_rows);
}

//Remove attributes & values according to user's anwser
function get_skip_cols(user_attr_array) {
  //Extract attributes bu groups from the json
  var user_attributes = [];
  for (attr_group of user_attr_array) {
    if (attr_group != null) {
      user_attributes = user_attributes.concat(attr_group_obj[attr_group]);
    }
  }
  user_attributes = user_attributes.concat(attr_group_obj['other']); // add the attributes grouped in other anyway

  var skip_col_arr = [];
  for (var col_id = 0; col_id < attr_header.length; col_id++) {
    if (!user_attributes.includes(attr_header[col_id])) {
      skip_col_arr.push(col_id);
    }
  }

  return skip_col_arr;
}

// Request files using ajax
function loadDoc(url) {
  var ajax = new XMLHttpRequest();
  ajax.onreadystatechange = function() {
    if (ajax.readyState === 4 && ajax.status == 200) {
      if (url == 'data/attribute_group.json') attr_group_obj = JSON.parse(ajax.responseText);
      else if (url == 'data/d_flower_data_mapped.tsv') process_plant_tsv(ajax.responseText);
      else read_map_tsv(ajax.responseText);
    }
  };

  ajax.open('GET', url, true);
  ajax.send(null);
}
