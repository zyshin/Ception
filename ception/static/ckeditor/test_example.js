/**
 * Created by scyue on 16/4/8.
 */

function text_function() {
  CKEDITOR.config.height = 200;
  CKEDITOR.config.width = 'auto';
  var sentence_div = document.getElementById("selected-sentence");
  var id_div = document.getElementById("selected-id");
  var whole_text = document.getElementById("origin-text");
  var origin_id_div = document.getElementById("selected-id-original");
  var display_div = document.getElementById("display");

  function update_information() {
    var selected = editor.getSelectedSentence();
    sentence_div.innerHTML = selected.sentence;
    id_div.innerText = selected.id;
    whole_text.innerHTML = editor.getData();
  }

  function update_original() {

  }

  var editor = initWithLite('editor', true, false);
  editor.update_functions.push(update_information);

  var original = initWithLite('original', true, true);
  original.update_functions.push(update_original);
}
