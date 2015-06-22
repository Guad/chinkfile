$(document).ready(function()
{
	var theform = document.getElementById('mainform');
	var fileSelect = document.getElementById('files');
	var uploadButton = document.getElementById('sub');
	var fileDisplay = document.getElementById('fileDisplay');
	$('#button-about').attr('href', '#aboutmodal');
	$('#button-about').leanModal();

	theform.onsubmit = function(event) {
		event.preventDefault();
		var files = fileSelect.files;
		if(files.length === 0) {
			alertCard('No files');
		} else {
			var ltotal = total + files.length - 1;
			for (i = files.length - 1; i >= 0; i--) {
				var _id = i + ltotal;
				var file = files[i];
				if(file.size > 50 * 1024 * 1024) {
					fileAlertCard(file.name, 'File too large!');
					ltotal -= 1;
				} else {
					fileCard(file.name, _id);
					ltotal -= 1;
				}				
			}
			processFilesRecursively(files)
		}
	}
});

function showFiles(){
	fileDisplay.style.display="block";
	fileDisplay.textContent += document.getElementById('files').files[0].name + " ";
}

var fadeTime = 2000;
var gCounter = 0;
var total = 0;
function processFilesRecursively(fileArray)
{
	if(gCounter >= fileArray.length) {
		gCounter = 0;
		total += 1
		return 0;
	} else {
	var id = gCounter + total;
	var file = fileArray[gCounter];
	if(file.size > 10 * 1024 * 1024)
	{
		gCounter += 1;
		total += 1;
		processFilesRecursively(fileArray);
		return 0;
	}

	var formData = new FormData();

	formData.append('file[]', file, file.name);

	$('#file' + id + ' > div').removeClass('indeterminate');
	$('#file' + id + ' > div').addClass('determinate');

	var request = $.ajax({
		url: '/js',
		type: 'POST',
		async: true,
		data: formData,
		processData: false,
		contentType: false,
		xhr: function() {
			var myXhr = $.ajaxSettings.xhr();
        	if(myXhr.upload){
            	myXhr.upload.addEventListener('progress',function(e){
            		if(e.lengthComputable){
				        var max = e.total;
				        var current = e.loaded;
				        var Percentage = (current * 100)/max;
				        var divid = '#file' + id + ' > div';
				        $(divid).width(Percentage + '%');
					}  
            	}, false);
            }
        	return myXhr;
		},
		complete: function( jqXHR, textStatus) {
			//alert(textStatus);
			//console.log(jqXHR);
			var resp = jqXHR.responseText;
			var code = resp.split(":");
			
			if(code[0] === 'success') {
				$('<span class="badge"><a target="_blank" href="' + code[1] +'">' + code[2] + '</a></span><a>upload complete!</a>').insertAfter('#file' + id);
			}
			else if(code[0] === 'exists') {
				$('<span class="badge"><a target="_blank" href="' + code[1] + '">' + code[2] + '</a></span><a>Duplicate!</a>').insertAfter('#file' + id);
			}
			else if(code[0] === 'error') {
				$('<p>Invalid filename.</p>').insertAfter('#file' + id);
			}						
			$('#file' + id).fadeOut(1000);
			gCounter += 1;
			total += 1;
			processFilesRecursively(fileArray);
		},
		error: function(jqXHR, textStatus, errorThrown) {
			alertCard(errorThrown);
			gCounter += 1;
			total += 1;
			processFilesRecursively(fileArray);
		}
	});
	}
}

function fileCard(filename, id) {
	var start = '<div class="row card-out"><div class="col s12 l6 offset-l3 m8 offset-m2"><div class="card ';
	var color = 'blue-grey ';
	var inter = 'darken-1 z-depth-2"><div class="card-content white-text">'
	var head = '<h5 class="truncate">';
	var name =  filename;
	var action = '</h5></div><div class="card-action">';
	var progress = '<div class="progress" id="file' + id + '"><div class="indeterminate"';
	//var percentage = '20';
	var progress2 = '></div></div>';
	var actionend = '</div>';
	var inter2 = '';
	var end = '</div></div></div>';

	var div = $(start +
				color +
				inter +
				head +
				name +
				action +
				progress +
				progress2 +
				actionend +
				inter2 +
				end
				);
	
	div.hide();
	div.insertAfter('#afterthis');
	div.fadeIn(fadeTime);
}

function fileAlertCard(filename, text) {
	var start = '<div class="row card-out"><div class="col s12 l6 offset-l3 m8 offset-m2"><div class="card ';
	var color = 'blue-grey ';
	var inter = 'darken-1 z-depth-2"><div class="card-content white-text">'
	var head = '<h5 class="truncate">';
	var name =  filename;
	var action = '</h5></div><div class="card-action">';
	var progress2 = '<a>' + text + '</a></div>';
	var actionend = '</div>';
	var inter2 = '';
	var end = '</div></div></div>';

	var div = $(start +
				color +
				inter +
				head +
				name +
				action +
				progress2 +
				actionend +
				inter2 +
				end
				);
	
	div.hide();
	div.insertAfter('#afterthis');
	div.fadeIn(fadeTime);
}

function alertCard(text) {
	var start = '<div class="row card-out"><div class="col s12 l6 offset-l3 m8 offset-m2"><div class="card ';
	var color = 'orange ';
	var inter = 'darken-1 z-depth-2"><div class="card-content white-text">'
	var head = '<h5 class="truncate">';
	var icon = '<i class="small mdi-alert-warning" style="margin-right: 2%;"></i>';
	var name =  text;
	var inter2 = '</h5></div>';
	var end = '</div></div></div>';

	var div = $(start +
				color +
				inter +
				head +
				icon +
				name +
				inter2 +
				end
				);
	
	div.hide();
	div.insertAfter('#afterthis');
	div.fadeIn(fadeTime);
	div.delay(4000).fadeOut(fadeTime);
}
