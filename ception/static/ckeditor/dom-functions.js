/**
 * Created by scyue on 16/4/8.
 */


/*
 Check if current node is a PD Tag
 Return:
 0: false;
 1: PD
 -1: deleted PD;
 */
CKEDITOR.dom.node.prototype.isPD = function () {
  if (this.getName && this.getName() == "pd") {
    if (this.getChildren().getItem(0) instanceof CKEDITOR.dom.text) {
      return 1;
    } else {
      return -1;
    }
  } else if (this instanceof CKEDITOR.dom.text) {
    var p = this.getParent();
    if (p.getName && p.getName() == "pd") {
      return 1;
    }
  } else {
    return 0;
  }
};

CKEDITOR.dom.node.prototype.getUndergroundFirstNode = function () {
  if (this instanceof CKEDITOR.dom.node) {
    if (this instanceof CKEDITOR.dom.text) {
      return this;
    } else if (this instanceof CKEDITOR.dom.element) {
      if (this.getName() == "del" || this.isPD()) {
        return this;
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

CKEDITOR.dom.node.prototype.getUndergroundLastNode = function () {
  if (this instanceof CKEDITOR.dom.node) {
    if (this instanceof CKEDITOR.dom.text) {
      return this;
    } else if (this instanceof CKEDITOR.dom.element) {
      if (this.getName() == "del" || this.isPD()) {
        return this;
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
  } else {
    var node = this.getParent();
    while (node) {
      if (node.hasNext()) {
        next_big_node = node.getNext();
        break;
      }
      node = node.getParent();
    }
  }
  if (!next_big_node) return null;
  return next_big_node.getUndergroundFirstNode();
};

CKEDITOR.dom.node.prototype.getPreviousUndergroundNode = function () {
  var previous_big_node = undefined;
  if (this.hasPrevious()) {
    previous_big_node = this.getPrevious();
  } else {
    var node = this.getParent();
    while (node) {
      if (node.hasPrevious()) {
        previous_big_node = node.getPrevious();
        break;
      }
      if (node.getName() == "p") break;
      node = node.getParent();
    }
  }
  if (!previous_big_node) return null;
  return previous_big_node.getUndergroundLastNode();
};

CKEDITOR.dom.node.prototype.getNextPDNode = function () {
  var forward_node = this.getNextUndergroundNode();
  while (forward_node && !(forward_node.isPD() == 1)) {
    forward_node = forward_node.getNextUndergroundNode();
  }
  return forward_node;
};

CKEDITOR.dom.node.prototype.getSentenceID = function () {
  var sentence_id = undefined;
  if (this.getName && this.getName() == "pd") {
    sentence_id = parseInt(this.getAttribute('sid'));
  } else {
    var p = this.getParent();
    if (p.getName && p.getName() == "pd") {
      sentence_id = parseInt(p.getAttribute('sid'));
    }
  }
  return sentence_id;
};


CKEDITOR.editor.prototype.getSelectedSentence = function () {
  var node = this.getSelection().getRanges()[0].startContainer;
  var node_list = [];
  var forward_node = node;
  var backward_node = node.getPreviousUndergroundNode();
  while (backward_node && !(backward_node.isPD() == 1)) {
    node_list.unshift(backward_node);
    backward_node = backward_node.getPreviousUndergroundNode();
  }
  while (forward_node && !(forward_node.isPD() == 1)) {
    node_list.push(forward_node);
    forward_node = forward_node.getNextUndergroundNode();
  }
  var sentence_id = undefined;
  if (forward_node) {
    node_list.push(forward_node);
    sentence_id = forward_node.getSentenceID();
  }
  var text = "";
  for (var i = 0; i < node_list.length; i++) {
    if ((node_list[i].getName && node_list[i].getName() == "del") || node_list[i].isPD() < 0) {
      text += "<del>" + node_list[i].getText() + "</del>";
    } else {
      if (node_list[i].getParent() && node_list[i].getParent().getName && node_list[i].getParent().getName() == "ins") {
        text += "<ins>" + node_list[i].getText() + "</ins>";
      } else {
        text += node_list[i].getText();
      }
    }
  }
  return {
    sentence: text,
    id: sentence_id
  };
};


CKEDITOR.editor.prototype.feedVersion = function (content) {

};
