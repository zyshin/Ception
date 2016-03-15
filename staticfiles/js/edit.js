/**
 * Created by scyue on 16/3/14.
 */

function initEditPage(version_id, current_user, json_str_array, counter) {
  var get_sentence_comment = function (version_id, sentence_id, comment_div) {
    $.ajax({
      url: '/articles/sentence_return/',
      data: "version_id=" + version_id + "&sentence_id=" + sentence_id,
      cache: false,
      type: 'get',
      success: function (data) {
        comment_div.innerHTML = data;
        var comment_count = $("#comment-list .comment").length;
        $(".comment-count").text(comment_count);
        $("#sentence-comment").val("");
        $("#sentence-comment").blur();
      }
    });
  };

  var update_comments_and_divs = function () {
    if (previous_selected_id == -1) {
      for (var i = 0; i < block_array.length; i++) {
        block_array[i].removeAttribute("hidden");
      }
    }
    var selected = editor.getSelectedSentence();
    sentence_div.innerHTML = selected.sentence;
    id_div.innerHTML = selected.id;
    if (selected.id != previous_selected_id) {
      for (i = 0; i < sentence_id_form_array.length; i++) {
        sentence_id_form_array[i].setAttribute("value", selected.id);
      }
      for (i = 0; i < json_array.length; i++) {
        if (json_array[i].author == current_user) continue;
        var compare_div = document.getElementById("c-" + json_array[i].author);
        var comment_div = document.getElementById("t-" + json_array[i].author);

        var found_flag = false;
        for (var j = 0; j < json_array[i].sentence.length; j++) {
          var s = json_array[i].sentence[j];
          if (selected.id == s.id) {
            get_sentence_comment(json_array[i].id, s.id, comment_div);
            compare_div.innerHTML = s.content;
            found_flag = true;
            break;
          }
        }
        if (!found_flag) {
          compare_div.innerHTML = "Not Found"
        }
      }
    }
    previous_selected_id = selected.id;
  };

  CKEDITOR.config.height = 250;


  var editor = initWithLite("id_content", true, false);
  editor.sCount = counter;
  var sentence_div = document.getElementById("selected-sentence");
  var id_div = document.getElementById("selected-id");

  var sentence_id_form_array = [];
  var block_array = [];


  var json_array = [];
  for (var i = 0; i < json_str_array.length; i++) {
    json_array.push(JSON.parse(json_str_array[i]));
  }
  for (i = 0; i < json_array.length; i++) {
    var version_id_form = document.getElementById("version_id-" + json_array[i].author);
    version_id_form.setAttribute("value", json_array[i].id);
    sentence_id_form_array.push(document.getElementById("sentence_id-" + json_array[i].author));
    var block = document.getElementById("block-" + json_array[i].author);
    block.setAttribute("hidden", "hidden");
    block_array.push(block);
  }

  var previous_selected_id = -1;
  editor.on('contentDom', function () {
    this.document.on('click', function (event) {
      update_comments_and_divs();
    });
  });
  editor.on('key', function (e) {
    var key = sanitizeKeyCode(e.data.keyCode);
    if (key > 36 && key <= 40) {
      update_comments_and_divs();
    }
  });

  editor.on('change', function (e) {
    var selected = editor.getSelectedSentence();
    sentence_div.innerHTML = selected.sentence;
  });

  editor.on('drop', function (e) {
    console.log("This is drop");
    e.cancel();
  });

}