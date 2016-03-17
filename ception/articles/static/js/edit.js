/**
 * Created by scyue on 16/3/14.
 */

$(function () {
  var class_sentence_comment_form = $(".sentence-comment-form");
  class_sentence_comment_form.focus(function () {
    $(this).attr("rows", "2");
    $("#comment-helper").fadeIn();
  });
  class_sentence_comment_form.blur(function () {
    $(this).attr("rows", "1");
    $("#comment-helper").fadeOut();
  });
  class_sentence_comment_form.keydown(function (evt) {
    var keyCode = evt.which ? evt.which : evt.keyCode;
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      //console.log($("#comment-form").serialize());
      var block = $(this).closest(".sentence-block");
      $.ajax({
        url: '/articles/sentence_comment/',
        data: $(".sentence-comment-form", block).serialize(),
        cache: false,
        type: 'post',
        success: function (data) {
          $(".sentence-comment-list", block).html(data);
          $(".comment-count", block).text($(".sentence-comment-list", block).length);
          $(".sentence-comment-form", block).val("").blur();
        }
      });
    }
  });

  $(".sentence-comment-button").click(function () {
    var block = $(this).closest(".sentence-block");
    var comment_block = $(".sentence-comment-block", block);
    if (comment_block.css('display') == "none") {
      comment_block.fadeIn('normal');
    } else {
      comment_block.fadeOut('normal');
    }
  });
});


function initEditPage(current_version, current_user, json_str_array, counter) {
  var get_sentence_comment = function (version_id, sentence_id, block) {
    var csrf = $("input[name='csrfmiddlewaretoken']", block).val();
    $.ajax({
      url: '/articles/sentence_return/',
      data: {
        'version_id': version_id,
        'sentence_id': sentence_id,
        'csrfmiddlewaretoken': csrf
      },
      cache: false,
      type: 'post',
      success: function (data) {
        $(".sentence-comment-list", block).html(data);
        $(".comment-count", block).text($(".sentence-comment-list .sentence-comment", block).length);
        $(".sentence-comment-form", block).val("").blur();
      }
    });
  };

  var get_sentence_vote = function (version_id, sentence_id, author) {
    var block = $("#block-" + author);
    var csrf = $("input[name='csrfmiddlewaretoken']", block).val();
    $.ajax({
      url: '/articles/sentence_vote/',
      data: {},
      cache: false,
      type: 'post',
      success: function (data) {

      }
    });
  };

  var update_comments_and_divs = function () {
    if (previous_selected_id == -1) $("#sentence-list").removeAttr("hidden");

    var selected = editor.getSelectedSentence();
    current_sentence.html(selected.sentence);
    id_div.text(selected.id);
    if (selected.id != previous_selected_id) {
      for (i = 0; i < versions.length; i++) {
        var version = versions[i];
        $("input[name='sentence_id']", version.block).attr("value", selected.id);
        if (version.author == current_user) continue;
        var sentence_content = $(".sentence-content", version.block);
        var found_flag = false;
        for (var j = 0; j < version.sentence.length; j++) {
          var s = version.sentence[j];
          if (selected.id == s.id) {
            get_sentence_comment(version.id, s.id, version.block);
            sentence_content.html(s.content);
            found_flag = true;
            break;
          }
        }
        if (!found_flag) {
          sentence_content.text("Not Found");
        }
      }
      form_current_sentence_id.attr("value", selected.id);
      get_sentence_comment(current_version, selected.id, current_user_block);
    }
    previous_selected_id = selected.id;
  };

  CKEDITOR.config.height = 150;


  var editor = initWithLite("id_content", true, false);
  editor.sCount = counter;
  var current_user_block = $(".sentence-block[data-author='" + current_user + "']");
  current_user_block.addClass("selected-block");
  var current_sentence = $(".sentence-content", current_user_block);
  $(".time", current_user_block).text("current selected sentence");
  $("input[name='version_id']", current_user_block).attr("value", current_version);
  var id_div = $("#selected-id");
  var form_current_sentence_id = $("input[name='sentence_id']", current_user_block);

  var versions = [];
  for (var i = 0; i < json_str_array.length; i++) {
    versions.push(JSON.parse(json_str_array[i]));
  }

  for (i = 0; i < versions.length; i++) {
    versions[i].block = $(".sentence-block[data-author='" + versions[i].author + "']");
    $("input[name='version_id']", versions[i].block).attr("value", versions[i].id);
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
    current_sentence.text(selected.sentence);
  });

  editor.on('drop', function (e) {
    console.log("This is drop");
    e.cancel();
  });

}