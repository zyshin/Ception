/**
 * Created by scyue on 16/1/29.
 */

CKEDITOR.ENTER = 13;
CKEDITOR.BACKSPACE = 8;
CKEDITOR.INVISIABLECHAR = String.fromCharCode(0);
CKEDITOR.CUT_KEY = 1114200;
CKEDITOR.SHIFT_MAC = 2228240;

function sanitizeKeyCode(keyCode) {
    return keyCode & (~CKEDITOR.SHIFT) & (~CKEDITOR.ALT);
}

function isModifier(keyCode, modifier) {
    return (keyCode & modifier) == modifier;
}

function isVisible(keyCode) {
  var trueKeyCode = sanitizeKeyCode(keyCode);
  return (trueKeyCode >= 48 && trueKeyCode < 300) || trueKeyCode == 32;
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
  //console.log(node.getName());
  //console.log(node.getNext());
  if (node.getName() == "pd") {
    var new_text_node = new CKEDITOR.dom.text("\x00");
    new_text_node.insertAfter(node);
    newRange.moveToPosition(new_text_node, CKEDITOR.POSITION_BEFORE_END);
    newRange.select();
  }
}

// 0: false;
// -1: deleted PD;
// 1: PD
function isPD(node) {
  if (node instanceof CKEDITOR.dom.element && node.getName && node.getName() == "pd") {
    if (node.getChildren().getItem(0) instanceof CKEDITOR.dom.text) {
      return 1;
    } else {
      return -1;
    }
  } else if (node instanceof CKEDITOR.dom.text) {
    var p = node.getParent();
    if (p.getName && p.getName() == "pd") {
      return 1;
    }
  } else {
    return 0;
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

CKEDITOR.dom.node.prototype.getUndergroundFirstNode = function() {
  if (this instanceof CKEDITOR.dom.node) {
    if (this instanceof CKEDITOR.dom.text) {
      return this;
    } else if (this instanceof CKEDITOR.dom.element) {
      if (this.getName() == "del") {
        return this;
      } else if (isPD(this) == 1) {
        //console.log("This is normal PD");
        return this;
      } else if (isPD(this) == -1) {
        return this.getNextUndergroundNode();
      } else {
        return this.getFirst().getUndergroundFirstNode();
      }
    } else {
      alert("need check here");
    }

  } else {
    return undefined;
  }
};

CKEDITOR.dom.node.prototype.getUndergroundLastNode = function() {
  if (this instanceof CKEDITOR.dom.node) {
    if (this instanceof CKEDITOR.dom.text) {
      return this;
    } else if (this instanceof CKEDITOR.dom.element) {
      if (this.getName() == "del") {
        return this;
      } else if (isPD(this) == 1) {
        //console.log("This is normal PD");
        return this;
      } else if (isPD(this) == -1) {
        return this.getPreviousUndergroundNode();
      } else {
        return this.getLast().getUndergroundLastNode();
      }
    } else {
      alert("need check here");
    }

  } else {
    return undefined;
  }
};

CKEDITOR.dom.node.prototype.getNextUndergroundNode = function () {
  var next_big_node;
  if (this.hasNext()) {
    next_big_node = this.getNext();
    //console.log(previous_big_node);
  } else {
    var node = this.getParent();
    while (node) {
      if (node.hasNext()) {
        next_big_node = node.getNext();
        //console.log("There: " + next_big_node);
        break;
      }
      //if (node.getName() == "p") break;
      node = node.getParent();
    }
  }
  if (!next_big_node) {
    return null;
  }
  //console.log(next_big_node);
  var next_underground_node = next_big_node.getUndergroundFirstNode();
  //console.log(next_underground_node);
  if (next_underground_node && next_underground_node.getName && next_underground_node.getName() == "del") {
    return next_underground_node.getNextUndergroundNode();
  } else {
    return next_underground_node;
  }
};

CKEDITOR.dom.node.prototype.getPreviousUndergroundNode = function () {
  var previous_big_node;
  if (this.hasPrevious()) {
    previous_big_node = this.getPrevious();
    //console.log(previous_big_node);
  } else {
    var node = this.getParent();
    while (node) {
      if (node.hasPrevious()) {
        previous_big_node = node.getPrevious();
        //console.log("There: " + previous_big_node);
        break;
      }
      if (node.getName() == "p") break;
      node = node.getParent();
    }
  }
  if (!previous_big_node) {
    return null;
  }
  //console.log(previous_big_node);
  var previous_underground_node = previous_big_node.getUndergroundLastNode();
  //console.log(previous_underground_node);
  if (previous_underground_node && previous_underground_node.getName && previous_underground_node.getName() == "del") {
    return previous_underground_node.getPreviousUndergroundNode();
  } else {
    return previous_underground_node;
  }
};

CKEDITOR.dom.node.prototype.getNextPDNode = function () {
  var forward_node = this.getNextUndergroundNode();
  while (forward_node && !(isPD(forward_node) == 1)) {
    forward_node = forward_node.getNextUndergroundNode();
  }
  return forward_node;
};

CKEDITOR.editor.prototype.getSelectedSentence = function () {
  var node = this.getSelection().getRanges()[0].startContainer;
  var node_list = [];
  var forward_node = node;
  var backward_node = node.getPreviousUndergroundNode();
  //console.log(forward_node);
  //console.log(backward_node);
  while (backward_node && !(isPD(backward_node) == 1)) {
    //console.log(backward_node);
    node_list.unshift(backward_node);
    backward_node = backward_node.getPreviousUndergroundNode();
  }
  while (forward_node && !(isPD(forward_node) == 1)) {
    //console.log(forward_node);
    node_list.push(forward_node);
    forward_node = forward_node.getNextUndergroundNode();
  }
  //console.log(forward_node);
  var  sentence_id = undefined;
  if (forward_node) {
    //console.log(forward_node);
    node_list.push(forward_node);
    if (forward_node.getName && forward_node.getName() == "pd") {
      sentence_id = parseInt(forward_node.getId().slice(1));
    } else {
      var p = node.getParent();
      if (p.getName && p.getName() == "pd") {
        sentence_id = parseInt(p.getId().slice(1));
      }
    }
  }
  var text = "";
  for (var i = 0; i < node_list.length; i++) {
    //console.log(node_list[i]);
    text += node_list[i].getText();
  }

  return {
    sentence: text,
    id: sentence_id
  };
};

CKEDITOR.editor.prototype.getIDofSelectedSentence = function() {
  var node = this.getSelection().getRanges()[0].startContainer;
  var sentenceID;
  if (node instanceof CKEDITOR.dom.text) {
    while (node && node.getName && node.getName() != "pd") {
      node = node.getNext();
    }
    if (node && node.getName() == "pd") {
      sentenceID = parseInt(node.getId().substring(1));
    } else {
      alert("Error! No PD next");
    }
  } else if (node.getName() == "pd") {
    sentenceID = parseInt(node.getId().substring(1));
  } else {
    alert("No PD exist");
  }
  console.log("Sentence ID: " + sentenceID);
  return sentenceID;
};

CKEDITOR.editor.prototype.feedVersion = function (content) {

};

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
    editor.insertHtml("<pd id='" + stored_pd_id + "'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
    stored_pd.removeAttribute("prev_pd");
  } else {
    editor.insertHtml("<pd id='s" + (editor.sCount++) + "'>" + sentenceEnding.ending[e.data.keyCode] + "</pd>");
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