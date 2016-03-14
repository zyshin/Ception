$(function () {
  $(".publish").click(function () {
    $("input[name='status']").val("P");
    $("form").submit();
  });

  $(".draft").click(function () {
    $("input[name='status']").val("D");
    $("form").submit();
  });

  $(".preview").click(function () {
    $.ajax({
      url: '/articles/preview/',
      data: $("form").serialize(),
      cache: false,
      type: 'post',
      beforeSend: function () {
        $("#preview .modal-body").html("<div style='text-align: center; padding-top: 1em'><img src='/static/img/loading.gif'></div>");
      },
      success: function (data) {
        $("#preview .modal-body").html(data);
      }
    });
  });

  $("#comment").focus(function () {
    $(this).attr("rows", "3");
    $("#comment-helper").fadeIn();
  });

  $("#comment").blur(function () {
    $(this).attr("rows", "1");
    $("#comment-helper").fadeOut();
  });

  $("#comment").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      $.ajax({
        url: '/articles/comment/',
        data: $("#comment-form").serialize(),
        cache: false,
        type: 'post',
        success: function (data) {
          $("#comment-list").html(data);
          var comment_count = $("#comment-list .comment").length;
          $(".comment-count").text(comment_count);
          $("#comment").val("");
          $("#comment").blur();
        }
      });
    }
  });

  $(".sentence-comment").focus(function () {
    $(this).attr("rows", "2");
    $("#comment-helper").fadeIn();
  });

  $(".sentence-comment").blur(function () {
    $(this).attr("rows", "1");
    $("#comment-helper").fadeOut();
  });

  $(".sentence-comment").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      //console.log($("#comment-form").serialize());
      var author = $(this).attr("data-author");
      $.ajax({
        url: '/articles/sentence_comment/',
        data: $("#comment-form-" + author).serialize(),
        cache: false,
        type: 'post',
        success: function (data) {
          //console.log(data);
          $("#t-" + author).html(data);
          //var comment_count = $("#comment-list .comment").length;
          //$(".comment-count").text(comment_count);
          $(".sentence-comment").val("");
          $(".sentence-comment").blur();
        }
      });
    }
  });


});