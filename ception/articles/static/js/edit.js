/**
 * Created by scyue on 16/3/14.
 */
var global_editor;

function generate_alert(alert_type, content) {
  return '<div class="alert alert alert-' + alert_type + ' alert-dismissible fade in" role="alert">' +
      '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
      '<span aria-hidden="true">×</span>' + '</button>' +
      '<strong>' + content + '</strong>' + '</div>'
}

$(function () {
  var sentence_comment_content = $(".sentence-comment-content");
  sentence_comment_content.focus(function () {
    $(this).attr("rows", "2");
    $("#comment-helper").fadeIn();
  });
  sentence_comment_content.blur(function () {
    $(this).attr("rows", "1");
    $("#comment-helper").fadeOut();
  });
  sentence_comment_content.keydown(function (evt) {
    var content = $(this);
    var keyCode = evt.which ? evt.which : evt.keyCode;
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      //console.log($("#comment-form").serialize());
      var block = $(this).closest(".sentence-block");
      $.ajax({
        url: '/articles/sentence_comments/',
        data: $(".sentence-comment-form", block).serialize(),
        cache: false,
        type: 'post',
        success: function (data) {
          content.val("").blur();
          $(".sentence-comment-list", block).html(data);
          $(".comment-count", block).text($(".sentence-comment-list .sentence-comment", block).length);
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

  $(".sentence-vote").click(function () {
    var block = $(this).closest(".sentence-block");
    var this_span = $(this);
    var csrf = $("input[name='csrfmiddlewaretoken']", block).val();
    var version_id = $("input[name='version_id']", block).val();
    var sentence_id = $("input[name='sentence_id']", block).val();
    var vote = "";
    if ($(this).hasClass("voted")) {
      vote = "R";
    } else if ($(this).hasClass("up-vote")) {
      vote = "U";
    } else if ($(this).hasClass("down-vote")) {
      vote = "D";
    }
    $.ajax({
      url: '/articles/sentence_vote/',
      data: {
        'version_id': version_id,
        'sentence_id': sentence_id,
        'vote': vote,
        'csrfmiddlewaretoken': csrf
      },
      cache: false,
      type: 'post',
      success: function (data) {
        $(".sentence-vote", block).removeClass("voted");
        if (vote == "U" || vote == "D") {
          this_span.addClass("voted");
        }
        $(".sentence-comment-vote-number", block).text(data);
      }
    });
  });

  $("#cancel-button").click(function () {
    self.location = "/articles/" + $("#cancel-button").data("url");
  });

  $("#save-button").click(function () {
    var form = $("#edit_form");
    $.ajax({
      url: '/articles/edit/' + form.data('id') + '/',
      data: form.serialize() + "&action=save",
      cache: false,
      type: 'post',
      success: function (data) {
        console.log("Saved!");
      }
    });
  });

  $("#commit-button").click(function () {
    var form = $("#edit_form");
    $.ajax({
      url: '/articles/edit/' + form.data('id') + '/',
      data: {
        'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']", form).val(),
        'content': global_editor.getData(),
        'action': 'commit'
      },
      cache: false,
      type: 'post',
      success: function (data) {
        $("#side-col").prepend(generate_alert('success', 'Successfully Committed!'));
        $(".alert").fadeTo(2000, 500).slideUp(500, function () {
          $(".alert").alert('close');
        });
      }
    });
  });



});


function initEditPage(current_version, current_user, json_str_array, counter) {
  var get_sentence_comment = function (version_id, sentence_id, block) {
    var csrf = $("input[name='csrfmiddlewaretoken']", block).val();
    $.ajax({
      url: '/articles/sentence_comments/',
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
        $(".sentence-comment-content", block).val("").blur();
      }
    });
  };

  var get_sentence_vote = function (version_id, sentence_id, block) {
    var csrf = $("input[name='csrfmiddlewaretoken']", block).val();
    $.ajax({
      url: '/articles/sentence_vote/',
      data: {
        'version_id': version_id,
        'sentence_id': sentence_id,
        'csrfmiddlewaretoken': csrf
      },
      cache: false,
      type: 'post',
      success: function (data) {
        var data_json = JSON.parse(data);
        $(".sentence-comment-vote-number", block).text(data_json.count);
        $(".sentence-vote", block).removeClass("voted");
        if (data_json.state == "U") {
          $(".up-vote", block).addClass("voted");
        } else if (data_json.state == "D") {
          $(".down-vote", block).addClass("voted");
        }
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
        $("input[name='sentence_id']", version.block).val(selected.id);
        $(".time", version.block).text(version.time);
        if (version.author == current_user) continue;
        var sentence_content = $(".sentence-content", version.block);
        var found_flag = false;
        for (var j = 0; j < version.sentence.length; j++) {
          var s = version.sentence[j];
          if (selected.id == s.id) {
            get_sentence_comment(version.id, s.id, version.block);
            get_sentence_vote(version.id, s.id, version.block);
            sentence_content.html(s.content);
            found_flag = true;
            break;
          }
        }
        if (!found_flag) {
          sentence_content.text("Deleted");
        }
      }
      form_current_sentence_id.val(selected.id);
      get_sentence_comment(current_version, selected.id, current_user_block);
      get_sentence_vote(current_version, selected.id, current_user_block);
    }
    previous_selected_id = selected.id;
  };

  CKEDITOR.config.height = 150;


  var editor = initWithLite("id_content", true, false);
  global_editor = editor;
  editor.sCount = counter;
  var current_user_block = $(".sentence-block[data-author='" + current_user + "']");
  current_user_block.addClass("selected-block");
  var current_sentence = $(".sentence-content", current_user_block);
  $(".time", current_user_block).text("current selected sentence");
  $("input[name='version_id']", current_user_block).val(current_version);
  var id_div = $("#selected-id");
  var form_current_sentence_id = $("input[name='sentence_id']", current_user_block);

  var versions = [];
  for (var i = 0; i < json_str_array.length; i++) {
    versions.push(JSON.parse(json_str_array[i]));
  }

  for (i = 0; i < versions.length; i++) {
    versions[i].block = $(".sentence-block[data-author='" + versions[i].author + "']");
    $("input[name='version_id']", versions[i].block).val(versions[i].id);
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
    e.cancel();
  });

}