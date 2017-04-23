$(function () {
  $.fn.count = function (limit) {
    var length = limit - $(this).val().length;
    var form = $(this).closest("form");
    if (length <= 0) {
      $(".form-group", form).addClass("has-error");
    }
    else {
      $(".form-group", form).removeClass("has-error");
    }
    $(".help-count", form).text(length);
  };
  function browserCheck(task) {
    var isOpera = window.navigator.userAgent.indexOf("OPR") > -1,
        isChrome = navigator.userAgent.indexOf('Chrome') > -1,
        isSafari = navigator.userAgent.indexOf("Safari") > -1;
    if (isChrome && isSafari) isSafari = false;
    if (isChrome && isOpera) isChrome = false;
    if (!isSafari && !isChrome) {
        alert('请使用Chrome或Safari浏览器进行试验，否则可能无法正常工作！');
    }
  };
  browserCheck();
});
