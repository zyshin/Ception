/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

// CKEDITOR.editorConfig = function( config ) {
// 	// Define changes to default configuration here.
// 	// For complete reference see:
// 	// http://docs.ckeditor.com/#!/api/CKEDITOR.config
//
// 	// The toolbar groups arrangement, optimized for two toolbar rows.

CKEDITOR.editorConfig = function( config ) {
	config.toolbarGroups = [
		{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		// { name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
		// { name: 'links', groups: [ 'links' ] },
		// { name: 'insert', groups: [ 'insert' ] },
		// { name: 'forms', groups: [ 'forms' ] },
		// { name: 'tools', groups: [ 'tools' ] },
		{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
		// { name: 'others', groups: [ 'others' ] },
		// { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		// { name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
		// { name: 'styles', groups: [ 'styles' ] },
		// { name: 'colors', groups: [ 'colors' ] },
		{ name: 'lite', groups: [ 'lite' ] }
	];
	config.allowedContent = true;
	config.removePlugins = "elementspath";
	config.removeButtons = 'Copy,Cut,Paste,Source,Underline,Subscript,Superscript,Anchor,Image,Table,lite-toggletracking,lite-acceptall,lite-rejectall,lite-acceptone,lite-rejectone';
	config.extraPlugins = 'lite,save';
	config.format_tags = 'p;h1;h2;h3;pre';
	config.removeDialogTabs = 'image:advanced;link:advanced';
	config.undoStackSize = 200;
};
