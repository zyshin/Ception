/**
 * Created by scyue on 16/4/26.
 */

$(function () {
  $('#the-node').contextMenu({
    selector: 'li',
    callback: function (key, options) {
      var m = "clicked: " + key + " on " + $(this).text();
      window.console && console.log(m) || alert(m);
    },
    items: {
      "edit": {name: "Edit", icon: "edit"},
      "cut": {name: "Cut", icon: "cut"},
      "copy": {name: "Copy", icon: "copy"},
      "paste": {name: "Paste", icon: "paste"},
      "delete": {name: "Delete", icon: "delete"},
      "sep1": "---------",
      "quit": {
        name: "Quit", icon: function ($element, key, item) {
          return 'context-menu-icon context-menu-icon-quit';
        }
      }
    }
  });
});