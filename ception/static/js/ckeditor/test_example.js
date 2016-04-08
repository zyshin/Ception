/**
 * Created by scyue on 16/4/8.
 */

function text_function() {
  CKEDITOR.config.height = 200;
  CKEDITOR.config.width = 'auto';
  var editor = initWithLite('editor', true, false);

  function update_information() {
    var selected = editor.getSelectedSentence();
    sentence_div.innerHTML = selected.sentence;
    id_div.innerText = selected.id;
    origin_div.innerHTML = editor.getData();
  }

  var sentence_div = document.getElementById("selected-sentence");
  var id_div = document.getElementById("selected-id");
  var compare_div = document.getElementById("compare-sentence");
  var origin_div = document.getElementById("origin-text");
  editor.on('contentDom', function () {
    this.document.on('click', function (event) {
      update_information();
    });
  });
  editor.on('key', function (e) {
    update_information();
    var keycode = sanitizeKeyCode(e.data.keyCode);
    var range = editor.getSelection().getRanges()[0];
    var container = range.startContainer;
    var parent = container.getParent();
    if (keycode == CKEDITOR.BACKSPACE && container.getLength && parent.getName() == "ins") {
      var tar_n = parent && parent.hasNext() && parent.getNext().getName && parent.getNext().getName() == "del";
      var ending = (range.startOffset == container.getText().length);
      var tar_p = parent && parent.hasPrevious() && parent.getPrevious().getName && parent.getPrevious().getName() == "del";
      var beginning = (range.startOffset == 1);
      var same = (range.startOffset == range.endOffset);
      var inside_ins = (parent.getName() == "ins");
      if (inside_ins && same) {
        if (tar_n && ending) {
          if (range.startOffset > 1) {
            container.setText(container.getText().slice(0, -1));
            range.startOffset -= 1;
            range.endOffset -= 1;
          } else {
            var previous = parent.getPreviousUndergroundNode();
            range.setStart(previous, previous.getLength());
            range.setEnd(previous, previous.getLength());
            container.remove();
          }
          editor.getSelection().selectRanges([range]);
          editor.fire('change');
          e.cancel();
        } else if (tar_p && beginning) {
          var previous = parent.getPreviousUndergroundNode();
          range.setStart(previous, previous.getLength());
          range.setEnd(previous, previous.getLength());
          container.remove();
          editor.getSelection().selectRanges([range]);
          editor.fire('change');
          e.cancel();
        }
      }
    }
  });
  editor.on('change', function (e) {
    update_information();
  });
}
