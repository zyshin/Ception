/// <reference path="../App.js" />
//document.write("<script language=javascript src='https://appsforoffice.microsoft.com/lib/1/hosted/office.js'></script>");

(function () {
    "use strict";

    // The initialize function must be run each time a new page is loaded
    Office.initialize = function (reason) {
        $(document).ready(function () {
            app.initialize();
            // wire up event handler
            $("#showHtml").click(onShowHtml);
            $("#showXML").click(onShowXML);
            $("#addContentHellowWorld").click(onAddContentHellowWorld);
            $('#addContentHtml').click(onAddContentHtml);
            $('#addContentMatrix').click(onAddContentMatrix);
            $('#addContentOfficeTable').click(onAddContentOfficeTable);
            $('#addContentOfficeOpenXml').click(onAddContentOfficeOpenXml);
        });
    };
    
    function onShowHtml() {
        Word.run(function (context) {

            // Create a proxy object for the document body.
            var body = context.document.body;

            body.insertHtml('<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title></title><meta charset="utf-8" /><style type="text/css">div:before{content:"[ ";}div::after{content:" ]";}div{color:aqua;}</style></head><body><div>This is a test.</div></body></html>', Word.InsertLocation.end);
            // Queue a commmand to get the HTML contents of the body.
            var bodyHTML = body.getHtml();
            return context.sync().then(function () {
                write("Body HTML contents: " + bodyHTML.value);
                // console.log("Body HTML contents: " + bodyHTML.value);
            });
        })
    }

    function onShowXML() {
        Word.run(function (context) {

            // Create a proxy object for the document body.
            var body = context.document.body;

            // Queue a commmand to get the OOXML contents of the body.
            var bodyOOXML = body.getOoxml();

            // Synchronize the document state by executing the queued commands,
            // and return a promise to indicate task completion.
            return context.sync().then(function () {
                write("Body OOXML contents: " + bodyOOXML.value);
            });
        })
    }

    function onAddContentHellowWorld() {
         //Office.context.document.setSelectedDataAsync("Hello World!", testForSuccess);
         //console.log("Here");
        // sendFile();
        Office.context.document.getSelectedDataAsync(Office.CoercionType.Text, function (asyncResult) {
            if (asyncResult.status == Office.AsyncResultStatus.Failed) {
                write('Action failed. Error: ' + asyncResult.error.message);
            }
            else {
                write('Selected data: ' + asyncResult.value);
            }
        });
    }

    // Function that writes to a div with id='message' on the page.
    function write(message) {
        document.getElementById('message').innerText += message;
    }

    function onAddContentHtml() {
/*        // create HTML element
        var div = $("<div>")
				.append($("<h2>").text("My Heading"))
				.append($("<p>").text("This is paragraph 1"))
				.append($("<p>").text("This is paragraph 2"))

        // insert HTML into Word document
        Office.context.document.setSelectedDataAsync(div.html(), { coercionType: "html" }, testForSuccess); */

        $.ajax({
            url: "TestPage2.html",
            type: "GET",
            dataType: "text",
            success: function (html) {
                Office.context.document.setSelectedDataAsync(html, { coercionType: "html" }, testForSuccess)
            }
        });

    }

    function onAddContentMatrix() {
        // create matrix as an array of arrays
        var matrix = [["First Name", "Last Name"],
	                  ["Bob", "White"],
	                  ["Anna", "Conda"],
	                  ["Max", "Headroom"]];

        // insert matrix into Word document
        Office.context.document.setSelectedDataAsync(matrix, { coercionType: "matrix" }, testForSuccess);
    }

    function onAddContentOfficeTable() {

        // create and populate an Office table
        var myTable = new Office.TableData();
        myTable.headers = [['First Name', 'Last Name']];
        myTable.rows = [['Bob', 'White'], ['Anna', 'Conda'], ['Max', 'Headroom']];

        // add table to Word document
        Office.context.document.setSelectedDataAsync(myTable, { coercionType: "table" }, testForSuccess)
    }

    function onAddContentOfficeOpenXml() {
        var fileName = $("#listOpenXmlContent").val();

        $.ajax({
            url: fileName,
            type: "GET",
            dataType: "text",
            success: function (xml) {
                Office.context.document.setSelectedDataAsync(xml, { coercionType: "ooxml" }, testForSuccess)
            }
        });
    }

    function testForSuccess(asyncResult) {
        if (asyncResult.status === Office.AsyncResultStatus.Failed) {
            app.showNotification('Error', asyncResult.error.message);
        }
    }
})();