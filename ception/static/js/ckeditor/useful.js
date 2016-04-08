/**
 * Created by scyue on 16/1/29.
 */

CKEDITOR.ENTER = 13;
CKEDITOR.BACKSPACE = 8;
CKEDITOR.INVISIABLECHAR = String.fromCharCode(0);
CKEDITOR.CUT_KEY = 1114200;
CKEDITOR.SHIFT_MAC = 2228240;

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

function fixSpecificDeleteBug(editor, e) {
  var keycode = e.data.keyCode;
  if (sanitizeKeyCode(keycode) == CKEDITOR.BACKSPACE) {
    if (isModifier(keycode, CKEDITOR.CTRL)) {
      e.cancel();
    }
  }
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

function fixSpecificBSBug(editor, e) {
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
          range.setStart(previous, previous.getLength());
          range.setEnd(previous, previous.getLength());
          container.remove();
        }
        editor.getSelection().selectRanges([range]);
        editor.fire('change');
        e.cancel();
      } else if (tar_p && beginning) {
        var previous = parent.getPreviousUndergroundNode();
        range.setStart(previous, previous.getLength());
        range.setEnd(previous, previous.getLength());
        container.remove();
        editor.getSelection().selectRanges([range]);
        editor.fire('change');
        e.cancel();
      }
    }
  }
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


function getPDNodeIfExist(node) {
  if (node instanceof CKEDITOR.dom.element && node.getName && node.getName() == "pd") {
    if (node.getChildren().getItem(0) instanceof CKEDITOR.dom.text) {
      return node;
    } else {
      return undefined;
    }
  } else if (node instanceof CKEDITOR.dom.text) {
    var p = node.getParent();
    if (p.getName && p.getName() == "pd") {
      return p;
    }
  } else {
    return undefined;
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

function insertPDTag (editor, e) {
  var node = editor.getSelection().getRanges()[0].startContainer;
  var stored_pd = node.getNextPDNode();
  if (stored_pd && stored_pd.getAttribute("prev_pd")) {
    var stored_pd_id = stored_pd.getAttribute("prev_pd");
    editor.insertHtml("<pd sid='" + stored_pd_id + "'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
    stored_pd.removeAttribute("prev_pd");
  } else {
    editor.insertHtml("<pd sid='" + (editor.sCount++) + "'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
  }
}

function deletePDTag (editor, e) {
  var node = editor.getSelection().getRanges()[0].startContainer;
  var pd = getPDNodeIfExist(node);
  if (pd) {
    var next_pd = pd.getNextPDNode();
    if (next_pd) {
      console.log(pd);
      next_pd.setAttribute("prev_pd", pd.getId());
    }
  }
}


function ceptArming(editor) {
  editor.on('key', function(e) {
    fixSpecificLineBug(editor, e);
    fixSpecificCutBug(editor, e);
    fixSpecificBSBug(editor, e);
    fixSpecificDeleteBug(editor, e);
    if (isVisible(e.data.keyCode)) {
      avoidPDtag(editor, e);
    }
    //editor.getIDofSelectedSentence();
    if (sentenceEnding(e.data.keyCode)) {
      insertPDTag(editor, e);
      e.cancel();
    }
    if (e.data.keyCode == CKEDITOR.BACKSPACE) {
      deletePDTag(editor, e);
    }
  });
}

function initWithLite(name, isTracking, isShowing) {
  editor = CKEDITOR.replace(name);
  editor.on(LITE.Events.INIT, function(e) {
    editor.lite = e.data.lite;
    editor.lite.toggleTracking(isTracking);
    editor.lite.toggleShow(isShowing);
  });
  ceptArming(editor);
  return editor;
}