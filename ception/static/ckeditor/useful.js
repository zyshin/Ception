/**
 * Created by scyue on 16/1/29.
 */

CKEDITOR.ENTER = 13;
CKEDITOR.BACKSPACE = 8;
CKEDITOR.DELETE = 46;
CKEDITOR.INVISIABLECHAR = String.fromCharCode(0);
CKEDITOR.CUT_KEY = 1114200;
CKEDITOR.SHIFT_MAC = 2228240;

CKEDITOR.SENTENCE_NEW = -10;
CKEDITOR.SENTENCE_SPLIT = -9;
CKEDITOR.SENTENCE_UNDEFINED = -1;

function sanitizeKeyCode(keyCode) {
  return keyCode & (~CKEDITOR.SHIFT) & (~CKEDITOR.ALT) & (~CKEDITOR.CTRL);
}

function isModifier(keyCode, modifier) {
    return (keyCode & modifier) == modifier;
}

function isVisible(keyCode) {
  var trueKeyCode = sanitizeKeyCode(keyCode);
  return (trueKeyCode >= 48 && trueKeyCode < 300) || trueKeyCode == 32;
}

function fixSpecificCtrlBsBug(editor, e) {
  var keycode = e.data.keyCode;
  if (sanitizeKeyCode(keycode) == CKEDITOR.BACKSPACE) {
    if (isModifier(keycode, CKEDITOR.CTRL)) {
      e.cancel();
    }
  }
}

//TODO: Naive fix of Delete Bug
function fixSpecificCtrlDeleteBug(editor, e) {
  var keycode = e.data.keyCode;
  if (sanitizeKeyCode(keycode) == CKEDITOR.DELETE) {
    if (isModifier(keycode, CKEDITOR.CTRL)) {
      e.cancel();
    }
  }
}

//TODO: Naive fix of Ctrl+Delete Bug
function fixSpecificDeleteBug(editor, e) {

}

function fixSpecificLineBug(editor, e) {
    var keycode = sanitizeKeyCode(e.data.keyCode);
    if (keycode == CKEDITOR.ENTER) {
        ceptArming.hasEntered = true;
    } else if (ceptArming.hasEntered && keycode >= 33 && keycode <= 126) {
        var range = editor.getSelection().getRanges()[0];
        var startNode = range.startContainer;
        if (editor.lite.isTracking) {
            var parentString = startNode.getParent().getText();
            if (parentString.length == 1 && parentString.charCodeAt(0) == 8203) {
                startNode.setText(CKEDITOR.INVISIABLECHAR);
                range.moveToElementEditablePosition( startNode );
                editor.getSelection().selectRanges( [ range ] );
            }
        }
        ceptArming.hasEntered = false;
    }
}

function fixSpecificBsBug(editor, e) {
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
          while ((previous.getName && previous.getName() == "del") || previous.isPD() == -1) {
            previous = previous.getPrevious();
          }
          range.setStart(previous, previous.getLength());
          range.setEnd(previous, previous.getLength());
          container.remove();
        }
        editor.getSelection().selectRanges([range]);
        e.cancel();
      } else if (tar_p && beginning) {
        if (container.getLength() == 1) {
          container.remove();
        } else {
          container.setText(container.getText().slice(1));
        }
        var previous = parent.getPreviousUndergroundNode();
        while ((previous.getName && previous.getName() == "del") || previous.isPD() == -1) {
          console.log(previous.getName());
          previous = previous.getPrevious();
        }
        range.setStart(previous, previous.getLength());
        range.setEnd(previous, previous.getLength());
        editor.getSelection().selectRanges([range]);
        e.cancel();
      }
    }
  }
  editor.fire('scyue_event');
}

function fixSpecificCutBug(editor, e) {
  if (e.data.keyCode === CKEDITOR.CUT_KEY) {
    alert("Cut function is disabled due to unsolvable bug. " +
        "Please use the combination of Copy and Delete instead.");
    e.cancel();
  }
}

function avoidPDtag(editor, e) {
  //editor = CKEDITOR.editor();
  var range = editor.getSelection().getRanges()[0];
  var newRange = editor.createRange();
  var node = range.startContainer;
  //console.log(node);
  if (node instanceof CKEDITOR.dom.text) {
    node = node.getParent();
  }
  if (node.getName && node.getName() == "pd") {
    var new_text_node = new CKEDITOR.dom.text("\x00");
    new_text_node.insertAfter(node);
    newRange.moveToPosition(new_text_node, CKEDITOR.POSITION_BEFORE_END);
    newRange.select();
  }
}




function sentenceEnding (keyCode) {
  for (var key in sentenceEnding.ending) {
    if (keyCode == key)
      return true;
  }
  return false;
}

sentenceEnding.ending = {
  190: ".",
  2228415: "?",
  2228273: "!"
};


//we treat all the insert as split
function insertPDTag (editor, e) {
  var node = editor.getSelection().getRanges()[0].startContainer;
  var next_pd = node.getNextPDNode();
  while (next_pd.getSentenceID() < 0) {
    next_pd = next_pd.getNextPDNode();
  }
  var rsid_array;
  if (next_pd && (rsid_array = eval(next_pd.getAttribute("rsid"))) && rsid_array.length > 0) {
    editor.insertHtml("<pd sid='" + rsid_array.pop() + "' replaced='true'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
    next_pd.setAttribute("rsid", "[" + rsid_array + "]");
  } else if (next_pd) {
    var sid = next_pd.getSentenceID();
    editor.insertHtml("<pd sid='" + CKEDITOR.SENTENCE_SPLIT + "' tsid='" + sid + "'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
  } else {
    editor.insertHtml("<pd sid='" + CKEDITOR.SENTENCE_NEW + "'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
  }
}


// We treat all the delete as merge
function deletePDTag (editor, e) {
  var node = editor.getSelection().getRanges()[0].startContainer;
  var pd = node.getPDNodeIfExist();
  if (pd) {
    var sid = pd.getSentenceID();
    if (sid >= 0) {
      var next_pd = pd.getNextPDNode();
      if (next_pd) {
        var rsid_array = [];
        if (next_pd.hasAttribute("rsid")) {
          rsid_array = eval(next_pd.getAttribute("rsid"));
        }
        rsid_array.push(sid);
        next_pd.setAttribute("rsid", "[" + rsid_array + "]");
      }
    }
  }
}


function ceptArming(editor) {
  editor.on('key', function(e) {
    fixSpecificLineBug(editor, e);
    fixSpecificCutBug(editor, e);
    fixSpecificBsBug(editor, e);
    fixSpecificCtrlBsBug(editor, e);
    fixSpecificDeleteBug(editor, e);
    fixSpecificCtrlDeleteBug(editor, e);
    if (isVisible(e.data.keyCode)) {
      avoidPDtag(editor, e);
    }
    //editor.getIDofSelectedSentence();
    if (sentenceEnding(e.data.keyCode)) {
      insertPDTag(editor, e);
      editor.fire('scyue_event');
      e.cancel();
    }
    if (e.data.keyCode == CKEDITOR.BACKSPACE) {
      deletePDTag(editor, e);
    }
  });
}

function set_editor_update_function(editor) {
  editor.update_functions = [];
  editor.on('contentDom', function () {
    this.document.on('click', function (event) {
      for (var i = 0; i < editor.update_functions.length; i++) {
        editor.update_functions[i]();
      }
    })
  });
  editor.on('key', function () {
    setTimeout(function () {
      for (var i = 0; i < editor.update_functions.length; i++) {
        editor.update_functions[i]();
      }
    }, 50);
  });
  editor.on('scyue_event', function () {
    for (var i = 0; i < editor.update_functions.length; i++) {
      editor.update_functions[i]();
    }
  });
}

function initWithLite(name, isTracking, isShowing) {
  var editor = CKEDITOR.replace(name);
  editor.on(LITE.Events.INIT, function(e) {
    editor.lite = e.data.lite;
    editor.lite.toggleTracking(isTracking);
    editor.lite.toggleShow(isShowing);
  });
  ceptArming(editor);
  set_editor_update_function(editor);
  return editor;
}