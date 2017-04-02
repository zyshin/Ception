/**
 * Created by scyue on 16/3/14.
 */
 // Fjllsjl;f

var versions = [];
var bank = null;
var summary_bank = null;

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

CKEDITOR.SAVE_KEY = 1114195;

function generate_alert(alert_type, content) {
  return '<div class="alert alert alert-' + alert_type + ' alert-dismissible fade in" role="alert">' +
      '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
      '<span aria-hidden="true">×</span>' + '</button>' +
      '<strong>' + content + '</strong>' + '</div>'
}

function firm() { 
        if (confirm("Do you want to save before you leave?")) {  
            commit_ajax();
            history.back();
            //alert("点击了确定");  
        }  
        else {  
          history.back();
            //alert("点击了取消");  
        }  
}   

function closeWin(){
 var exit = confirm("Do you want to save before you leave?");  
 console.log("sssswww");
     if(exit==true){
        commit_ajax();
        //do something before closing;
     }
  } 

$(function () {
  window.addEventListener("beforeunload", function (e) {
    var confirmationMessage = "\o/";
    console.log("p");
    window.open("http://www.baidu.com");
    e.returnValue = confirmationMessage;     // Gecko, Trident, Chrome 34+
    return confirmationMessage;              // Gecko, WebKit, Chrome <34
  });

  $.contextMenu({
    selector: '.replace',
    trigger: 'hover',
    delay: 200,
    autoHide: true,

    build: function ($trigger, e) {
      // this callback is executed every time the menu is to be shown
      // its results are destroyed every time the menu is hidden
      // e is the original contextmenu event, containing e.pageX and e.pageY (amongst other data)
      var current_using_bank = bank;
      var pk = $(e.currentTarget).data('pk');
      console.log("aaa");
      if ($(e.currentTarget).closest(".context-menu-activated").hasClass('summary-content')) {
        current_using_bank = summary_bank
      }
      var return_menu = {};
      $.each(current_using_bank[pk], function (index, bundle) {
        if (index != 0) {
          return_menu[bundle.key] = {
            name: bundle.word,
            icon: function (opt, $itemElement, itemKey, item) {
              // var indents = Number.isInteger(bundle.count)? '&nbsp;&nbsp;&nbsp;' : '';
              // $itemElement.html(indents + '<span class="label label-success" style="margin-right: 5px;">' +  bundle.count + '</span>' + indents + bundle.word + opt.selector);
             // $itemElement.html('<span class="label label-success" style="margin-right: 5px;">' +  bundle.count + '</span>' + bundle.word + opt.selector);
              $itemElement.html( bundle.word + opt.selector + '<font color=black>(' + bundle.count + ')</font>');

            }
          };
        } else {
          return_menu[bundle.key] = {
            name: bundle.word,
            icon: function (opt, $itemElement, itemKey, item) {
               console.log(bundle.word);
              // $itemElement.html('<span class="label label-info" style="margin-right: 5px;">' + (Number.isInteger(bundle.count)? 'origin' : bundle.count) + '</span>' + bundle.word + opt.selector);
       //       $itemElement.html('<span class="label label-info" style="margin-right: 5px;">' + bundle.count + '</span>' + bundle.word + opt.selector);
               $itemElement.html( bundle.word + opt.selector + '<font color=black>(' + bundle.count + ')</font>');

            }
          };
        }
      });
      return {
        callback: function (key, options) {
          this.html(key);
        },
        items: return_menu
      }
    }
  });

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
          console.log("abc");
          var version_id = $("input[name='version_id']", block).val();
          var sentence_id = $("input[name='sentence_id']", block).val();
          var version = undefined;
          for (var i = 0; i < versions.length; i++) {
            if (versions[i].id == version_id) {
              version = versions[i];
              //console.log(versions[i]);
            }
            //console.log(versions.length);
          }
          content.val("").blur();
          $(".sentence-comment-list", block).html(data).removeAttr("hidden");
          
          // console.log(version_id);
          // console.log("www");

          // added
          if(version != undefined){       
          version.comments[sentence_id]['html'] = data;
          version.comments[sentence_id]['count'] = $(".sentence-comment-list .sentence-comment", block).length;
          $(".comment-count", block).text(version.comments[sentence_id]['count']);
          //console.log("abcdd");
          }
          else{
              version = versions[0];
              version.comments[sentence_id]['html'] = data;
              version.comments[sentence_id]['count'] = $(".sentence-comment-list .sentence-comment", block).length;
              $(".comment-count", block).text(version.comments[sentence_id]['count']);
              //console.log("abcdd");
          }
        }
      });
    }
  });

  $(".sentence-comment-button").click(function () {
    console.log("aaa");
    var block = $(this).closest(".sentence-block");
    var comment_block = $(".sentence-comment-block", block);
    if (comment_block.css('display') == "none") {
      $(this).addClass('hovered');
      comment_block.fadeIn('normal');
    } else {
      $(this).removeClass('hovered');
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

        if(version != undefined){
            version.vote[sentence_id]['state'] = vote;
            $(".sentence-comment-vote-number", block).text(data);
            version.vote[sentence_id]['count'] = data;
        }
        else{
            version = versions[0];
            version.vote[sentence_id]['state'] = vote;
            $(".sentence-comment-vote-number", block).text(data);
            version.vote[sentence_id]['count'] = data;
        }
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
    //firm();
    commit_ajax();
  });

  // $("#cancel-button").click(function () {
  //   //firm();
  // });

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
      $(".sentence-content-others").css("display", "inline-block");
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

  $("#hide-del-modal").change(function () {
    if ($(this).prop('checked')) {
      $(".modal-sentence").removeClass("hide-del-class");
    } else {
      $(".modal-sentence").addClass("hide-del-class");
    }
  });


  var modal = $("#merge-modal");
  $(".accept-button").click(function () {
    var block = $(this).closest(".sentence-block");
    var my_sentence = $("#current_sentence").html();
    var csrf = $("input[name='csrfmiddlewaretoken']", block).val();
    var version_id = $("input[name='version_id']", block).val();
    var sentence_id = $("input[name='sentence_id']", block).val();

    $.ajax({
      url: '/articles/merge_api/',
      data: {
        'csrfmiddlewaretoken': csrf,
        'sen_A': my_sentence,
        'sen_B': $(".sentence-content", block).html(),
        'sen_id': sentence_id,
        'ver_id': version_id
      },
      cache: false,
      type: 'post',
      success: function (json) {
        var data = JSON.parse(json);
        bank = data.data;
        $(".modal-body", modal).html(data.str);
        merge_second_stage.csrf = csrf;
        merge_second_stage.ver_id = version_id;
        merge_second_stage.sen_id = sentence_id;
        modal.modal();
        //if (data.conflicted) {
        //} else {
        //merge_second_stage($(".modal-body", modal).html());
        //}
      }
    });
  });

  $("#modal-confirm-button").click(function () {
    modal.modal('hide');
    merge_second_stage($(".modal-body", modal).html());
    // Auto Up-vote
    var vote_button = $('.sentence-block').has('input[name="version_id"][value="' + merge_second_stage.ver_id.toString() + '"]').find('.up-vote');
    if (!vote_button.hasClass("voted")) {
      vote_button.click();
    }
  });
});

function merge_second_stage(new_sentence) {
  var editor = CKEDITOR.instances['id_content'];
  var whole_content = editor.getData();
  $.ajax({
    url: '/articles/merge_second_stage/',
    data: {
      'csrfmiddlewaretoken': merge_second_stage.csrf,
      'sentence': new_sentence,
      'content': whole_content,
      'sen_id': merge_second_stage.sen_id
    },
    cache: false,
    type: 'post',
    success: function (json) {
      var data = JSON.parse(json);
      try {
        editor.setData(data.content);
      } catch (e) {
        // ignore
      }
      $("#current_sentence").html(data.formal);
    }
  })


}

function init_page(current_version, current_user, json_str_array, summary_list) {
  var update_summary = function (sid) {
    summary_block.removeClass("hidden");
    var edited_total = 0, merged_total = 0, unedited = 0;
    for (var i = 0; i < versions.length; i++) {
      var s = versions[i].info[sid];
      if (s.edited) {
        edited_total++;
        if (s.single) merged_total++;
      } else {
        unedited++;
      }
    }
    if (sid > 0 && summary_list[sid].html_str) {
      summary_bank = summary_list[sid].data;
      summary_sentence.html(summary_list[sid].html_str);
      summary_block.removeClass('hidden');
      $('#summary-merge-button').removeClass('hidden');
      $('#summary-span').text(merged_total + " / " + edited_total + " merged");
    } else {
      summary_block.addClass('hidden');
      $('#summary-merge-button').addClass('hidden');
      summary_sentence.html('');
    }
    $("input[name='sentence_id']", ".summary-block").val(sid);
    if (unedited == 0) {
      $("#hided-number-panel").addClass('hidden');
    } else {
      $(".omitted-number").text(unedited);
      $("#hided-number-panel").removeClass('hidden');
    }
  };

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
        //if (! $("#toggle-sentence-view").prop('checked')) $(".cke_concise").css("display", "none");
        get_sentence_comment(current_version, selected.id);
        get_sentence_vote(current_version, selected.id);
        update_summary(selected.id);
        //$(".cke_concise").css("display", "block");
        for (i = 0; i < versions.length; i++) {
          var version = versions[i];
          $("input[name='sentence_id']", version.block).val(selected.id);
          // $(".time", version.block).text(version.time);
          if (version.author == current_user) continue;
          var sentence_content = $(".sentence-content", version.block);
          var s = version.info[selected.id];
          if (s.edited) {
            if (!s.single) {
              $(".accept-button", version.block).css("display", "none");
              version.block.css("border-left", "none");
            } else {
              $(".accept-button", version.block).css("display", "inline-block");
              if (!summary_block.hasClass('hidden')) {
                version.block.css("border-left", "10px solid white");   //lightblue
              } else {
                version.block.css("border-left", "none");
              }
            }
            version.block.removeAttr("hidden");
            get_sentence_comment(version, s.id);
            get_sentence_vote(version, s.id);
            sentence_content.html(s.sentence);
            //version.block.data("sentence", s.sentence_without_span);
            //version.block.data("context", s.context_without_span);
            var author_editor = CKEDITOR.instances["editor-" + version.author];
            $("iframe", "#cke_editor-" + version.author).contents().find("body")
                .addClass("cke_concise_body")
                .addClass("hide-del-class")
                .html(s.context);
            try {
              var range = new CKEDITOR.dom.range(editor.document);
              var element = author_editor.document.findOne("#current");
              range.selectNodeContents(element);
              range.scrollIntoView();
            } catch (e) {
              console.log(e);
              //TODO: ignore it
            }
          } else {
            version.block.attr("hidden", "hidden");
          }
        }
      } else {
        for (i = 0; i < versions.length; i++) {
          versions[i].block.attr("hidden", "hidden");
        }
        summary_block.addClass("hidden");
      }
      window.scrollTo(0, backup_scoll);
      form_current_sentence_id.val(selected.id);
    }
    previous_selected_id = selected.id;
  };

  CKEDITOR.config.height = 400;

  var editor = initWithLite("id_content", true, true);
  commit_ajax.editor = editor;


  current_version.block = $(".sentence-block[data-author='" + current_user + "']");
  current_version.block.addClass("selected-block");
  var current_sentence = $(".sentence-content", current_version.block);
  $(".time", current_version.block).text("");
  $("input[name='version_id']", current_version.block).val(current_version.id);
  var id_div = $("#selected-id");
  var form_current_sentence_id = $("input[name='sentence_id']", current_version.block);
  var summary_sentence = $(".sentence-content", ".summary-block");
  var summary_block = $(".summary-block");
  $("input[name='version_id']", ".summary-block").val($("#edit_form").data("id"));



  for (var i = 0; i < json_str_array.length; i++) {
    versions.push(JSON.parse(json_str_array[i]));
    versions[i].info = JSON.parse(versions[i].info);
  }
  for (i = 0; i < versions.length; i++) {
    versions[i].block = $(".sentence-block[data-author='" + versions[i].author + "']");
    $("input[name='version_id']", versions[i].block).val(versions[i].id);
  }
  var previous_selected_id = -1;
  editor.on('contentDom', function () {
    editor.editable().attachListener(editor.document, 'click', function () {
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
    try {
      update_comments_and_divs();
    } catch (e) {
      // ignore it
    }
  });
  editor.on('drop', function (e) {
    e.cancel();
  });

  editor.on('save', function (e) {
    commit_ajax();
    e.cancel();
  });

  editor.on('lite:showHide', function (e) {
    CKEDITOR.config.liteShowHide = e.data.show;
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