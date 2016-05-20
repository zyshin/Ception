/**
 * Created by scyue on 16/5/20.
 */


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

$(function () {

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


  $("#hide-del-toggle").change(function () {
    if ($(this).prop('checked')) {
      $("iframe", ".cke_editor_compare").contents().find("body").removeClass("hide-del-class");
    } else {
      $("iframe", ".cke_editor_compare").contents().find("body").addClass("hide-del-class");
    }
  });
});
