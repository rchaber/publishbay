/**
 * @license Copyright (c) 2003-2013, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.html or http://ckeditor.com/license
 */

// Toolbar button items:
// 'Source', 'Save', 'NewPage', 'DocProps', 'Preview', 'Print', 'Templates', 'document'
// 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'Undo', 'Redo'
// 'Find', 'Replace', 'SelectAll', 'Scayt'
// 'Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'
// 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat'
// 'NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote', 'CreateDiv', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', 'BidiLtr', 'BidiRtl'
// 'Link', 'Unlink', 'Anchor'
// 'CreatePlaceholder', 'Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe', 'InsertPre'
// 'Styles', 'Format', 'Font', 'FontSize'
// 'TextColor', 'BGColor'
// 'UIColor', 'Maximize', 'ShowBlocks'
// 'button1', 'button2', 'button3', 'oembed', 'MediaEmbed'
// 'About'


CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For the complete reference:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.
	// config.toolbarGroups = [
	// { name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
	// { name: 'editing', groups: [ 'find', 'selection', 'spellchecker' ] },
	// { name: 'links' },
	// { name: 'insert' },
	// { name: 'forms' },
	// '/',
	// { name: 'tools' },
	// { name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
	// '/',
	// { name: 'others' },
	// { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	// { name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
	// '/',
	// { name: 'styles' },
	// { name: 'colors' }
	// ];

	config.height='500px';

	// Remove some buttons, provided by the standard plugins, which we don't
	// need to have in the Standard(s) toolbar.
	// config.removeButtons = 'Print,Preview,Templates,Strike,Blockquote,Subscript,Superscript,Image,Table,BGColor,TextColor,Flash,Smiley,Iframe,PageBreak,Save,NewPage,DocProps,BidiLtr,BidiRtl,CreateDiv,ShowBlocks';

	config.removePlugins = 'elementspath';

	config.toolbar = [
		[ 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo' ],
		[ 'Find', 'Replace', 'SelectAll', 'Scayt' ],
		[ 'HorizontalRule', 'SpecialChar' ],
		[ 'Maximize' ],
		[ 'Source' ],
		[ 'Format' ],
		'/',
		[ 'Bold', 'Italic', 'Underline', 'RemoveFormat' ],
		[ 'NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ],
		[ 'Font', 'FontSize' ]
	];

	// config.uiColor = '#AADC6E';

	config.skin = 'moonocolor';

	// Se the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';

	// Make dialogs simpler.
	config.removeDialogTabs = 'image:advanced;link:advanced';
};
