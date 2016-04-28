/**
 * Created by scyue on 16/3/14.
 */

var versions = [];

var commit_ajax = function () {
  var form = $("#edit_form");
  $.ajax({
    url: '/articles/edit/' + form.data('id') + '/',
    data: {
      'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']", form).val(),
      'content': commit_ajax.editor.getData().replace(/\x00/g, ''),
      'action': 'commit'
    },
    cache: false,
    type: 'post',
    success: function (data) {
      $("header").append(generate_alert('success', 'Successfully Committed!'));
      $(".alert").fadeTo(2000, 500).slideUp(500, function () {
        $(".alert").alert('close');
      });
    }
  });
};

//TODO: @ssy cherry_pick
var cherry_pick = function (author, other_sentence, other_all, my_sentence, my_all) {
  alert("This is cherry pick function!" + "\n\n" + author + "\n\n" + other_sentence + "\n\n" + other_all + "\n\n" + my_sentence + "\n\n" + my_all);
  var new_all = my_all;
  return new_all;
};


CKEDITOR.SAVE_KEY = 1114195;

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
          var version_id = $("input[name='version_id']", block).val();
          var sentence_id = $("input[name='sentence_id']", block).val();
          var version = undefined;
          for (var i = 0; i < versions.length; i++) {
            if (versions[i].id == version_id) {
              version = versions[i];
            }
          }
          content.val("").blur();
          $(".sentence-comment-list", block).html(data).removeAttr("hidden");
          version.comments[sentence_id]['html'] = data;
          version.comments[sentence_id]['count'] = $(".sentence-comment-list .sentence-comment", block).length;
          $(".comment-count", block).text(version.comments[sentence_id]['count']);
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
        var version = undefined;
        for (var i = 0; i < versions.length; i++) {
          if (versions[i].id == version_id) {
            version = versions[i];
          }
        }
        $(".sentence-vote", block).removeClass("voted");
        if (vote == "U" || vote == "D") {
          this_span.addClass("voted");
        }
        version.vote[sentence_id]['state'] = vote;
        $(".sentence-comment-vote-number", block).text(data);
        version.vote[sentence_id]['count'] = data;

      }
    });
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
    commit_ajax();
  });

  $(document).on('keydown', function (e) {
    if (e.which == 83 && (e.metaKey || e.ctrlKey)) {
      commit_ajax();
      e.preventDefault();
    }
  });

  $("#toggle-sentence-view").change(function () {
    if ($(this).prop('checked')) {
      $(".sentence-content-others").css("display", "none");
      $(".cke_concise").css("display", "block");
    } else {
      $(".sentence-content-others").css("display", "inline");
      $(".cke_concise").css("display", "none");
    }
  });

  $("#hide-del-toggle").change(function () {
    if ($(this).prop('checked')) {
      $(".sentence-content").removeClass("hide-del-class");
      $("iframe", ".cke_concise").contents().find("body").removeClass("hide-del-class");
    } else {
      $(".sentence-content").addClass("hide-del-class");
      $("iframe", ".cke_concise").contents().find("body").addClass("hide-del-class");
    }
  });

  $(".accept-button").click(function () {
    var block = $(this).closest(".sentence-block");
    var author = block.data("author");
    var current = $("#current_sentence").html();
    var this_content = CKEDITOR.instances["id_content"].getData();
    cherry_pick(author, block.data("sentence"), block.data("context"), current, this_content);
  });

});


function init_page(current_version, current_user, json_str_array) {
  var get_sentence_comment = function (version, sentence_id) {
    var list = $(".sentence-comment-list", version.block);
    list.html(version.comments[sentence_id]['html']);
    var count = version.comments[sentence_id]['count'];
    $(".comment-count", version.block).text(count);
    $(".sentence-comment-content", version.block).val("").blur();
    if (count == 0) {
      list.attr("hidden", "hidden");
    } else {
      list.removeAttr("hidden");
    }
  };

  var get_sentence_vote = function (version, sentence_id) {
    var data = version.vote[sentence_id];
    $(".sentence-comment-vote-number", version.block).text(data.count);
    $(".sentence-vote", version.block).removeClass("voted");
    if (data.state == "U") {
      $(".up-vote", version.block).addClass("voted");
    } else if (data.state == "D") {
      $(".down-vote", version.block).addClass("voted");
    }
  };

  var update_comments_and_divs = function () {
    if (previous_selected_id == -1) $("#sentence-list").removeAttr("hidden");

    var selected = editor.getSelectedSentence();
    if (selected.id > 0) {
      current_sentence.html(selected.sentence);
    } else {
      current_sentence.html("<add>" + selected.sentence + "</add>")
    }
    var backup_scoll = window.pageYOffset || document.documentElement.scrollTop;
    id_div.text(selected.id);
    if (selected.id != previous_selected_id) {
      if (selected.id > 0) {
        //$(".cke_concise").css("display", "block");
        for (i = 0; i < versions.length; i++) {
          var version = versions[i];
          $("input[name='sentence_id']", version.block).val(selected.id);
          $(".time", version.block).text(version.time);
          if (version.author == current_user) continue;
          var sentence_content = $(".sentence-content", version.block);
          var s = version.info[selected.id];
          if (s.edited) {
            version.block.removeAttr("hidden");
            get_sentence_comment(version, s.id);
            get_sentence_vote(version, s.id);
            sentence_content.html(s.sentence);
            version.block.data("sentence", s.sentence_without_span);
            version.block.data("context", s.context_without_span);
            var author_editor = CKEDITOR.instances["editor-" + version.author];
            //author_editor.setData(s.context);
            $("iframe", "#cke_editor-" + version.author).contents().find("body").addClass("cke_concise_body").addClass("hide-del-class").html(s.context);
            try {
              var range = new CKEDITOR.dom.range(editor.document);
              var element = author_editor.document.findOne("#current");
              var iframe_window = $("iframe", "#cke_editor-" + version.author)[0].contentWindow;
              //range.moveToElementEditStart(element);
              //range.scrollIntoView();
              //var p1 = iframe_window.pageYOffset;
              //range.moveToElementEditEnd(element);
              range.selectNodeContents(element);
              range.scrollIntoView();
              //var p2 = iframe_window.pageYOffset;
              //if (p1 == 0) {
              //  iframe_window.scrollTo(0, 0);
              //} else {
              //  iframe_window.scrollTo(0, (p1 + p2) / 2);
              //}
            } catch (e) {
              console.log(e);
              //TODO: ignore it
            }



          } else {
            version.block.attr("hidden", "hidden");
          }
        }
        //if (! $("#toggle-sentence-view").prop('checked')) $(".cke_concise").css("display", "none");
      } else {
        for (i = 0; i < versions.length; i++) {
          versions[i].block.attr("hidden", "hidden");
        }
      }
      window.scrollTo(0, backup_scoll);
      form_current_sentence_id.val(selected.id);
      get_sentence_comment(current_version, selected.id);
      get_sentence_vote(current_version, selected.id);
    }
    previous_selected_id = selected.id;
  };

  CKEDITOR.config.height = 240;

  var editor = initWithLite("id_content", true, false);
  commit_ajax.editor = editor;


  current_version.block = $(".sentence-block[data-author='" + current_user + "']");
  current_version.block.addClass("selected-block");
  var current_sentence = $(".sentence-content", current_version.block);
  $(".time", current_version.block).text("current selected sentence");
  $("input[name='version_id']", current_version.block).val(current_version.id);
  var id_div = $("#selected-id");
  var form_current_sentence_id = $("input[name='sentence_id']", current_version.block);



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
      setTimeout(function () {
        update_comments_and_divs();
      }, 50);

    } else if (e.data.keyCode == CKEDITOR.SAVE_KEY) {
      commit_ajax();
      e.cancel();
    } else if (e.data.keyCode == CKEDITOR.BACKSPACE) {
      var current_node = editor.getSelection().getRanges()[0].endContainer;
      if (current_node instanceof CKEDITOR.dom.text) {
        var parent = current_node.getParent();
        if (parent.getName && parent.getName() == "pd") {
          if (parent.getNextPDNode() == null) {
            e.cancel();
          }
        }
      }
    }
  });
  editor.on('change', function (e) {
    var selected = editor.getSelectedSentence();
    current_sentence.html(selected.sentence);
  });
  editor.on('drop', function (e) {
    e.cancel();
  });
}

function init_sidebar(info_str_array) {
  var editing_info_array = [];
  for (var i = 0; i < info_str_array.length; i++) {
    editing_info_array.push(JSON.parse(info_str_array[i]));
  }
  var sentence_array = $(".side-block");
  for (var i = 0; i < sentence_array.length; i++) {
    $(".side-sentence", $(sentence_array[i])).text(editing_info_array[i].content);
    $(".edit-span", $(sentence_array[i])).text("Edit: " + editing_info_array[i].edit);
    $(".delete-span", $(sentence_array[i])).text("Delete: " + editing_info_array[i].delete);
  }
}