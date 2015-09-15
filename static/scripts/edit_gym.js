var endisable = function(name) {
    var el = document.getElementById(name);
    console.log(name);
    console.log(el);
    if (!el.disabled) {
	el.value = 0;
    }
    el.disabled = !el.disabled;
    //document.getElementById(name + "amount").disabled = !document.getElementById(name + "amount").disabled;
};
var updateInfo = function(id, sendGym) {
    if (id==="Equipment") {
	var $equipmentinfo = $("#equipment input[type='text']");
	var updateValue = {};
	//for (var i=0; i<$updateValue.length; i++) {
	$equipmentinfo.each(function() {
		console.log(this);
		updateValue[this.name] = $(this).val();
	    });
    }
    else if (id==="Hours") {
	var $hoursinfo = $("#hours input, #hours select");
	var updateValue = {}
	$hoursinfo.each(function() {
		updateValue[this.name] = $(this).val();
	    });
	console.log("updateValue dict:");
	console.log(updateValue);
    }
    else {
	var updateValue = document.getElementById(id).value;
    }
    console.log("first");
    console.log(document.getElementById("gymId").value)
    console.log(id);
    console.log(updateValue);
    if (sendGym) {
	console.log("sendgym");
	$.getJSON("https://api.foursquare.com/v2/venues/"+document.getElementById("gymId").value+"?client_id=L4UK14EMS0MCEZOVVUYX2UO5ULFHJN3EHOFVQFSW0Z1MSFSR&client_secret=YKJB0JRFDPPSGTHALFOEP5O1NDDATHKQ2IZ5RO2GOX452SFA&v=20130815", function(result, status) {
		if (status !== 'success') return alert('Request to Foursquare failed');
		console.log(result['response']['venue']);
		venueInfo = result['response']['venue']
		gym = {};
		gymId = venueInfo['id'];
		gymName = venueInfo['name'];
		lat = venueInfo['location']['lat'];
		lng = venueInfo['location']['lng'];
		address = venueInfo['location']['address'];
	    })
	.done(function() {
		console.log(gym);
		$.post("/api/updateinfo", {
			    "gymId": gymId,
				"gymName": gymName,
				"lat": lat,
				"lng": lng,
				"address": address,
			    "type": id,
			    "text": JSON.stringify(updateValue)
			    })
		    .done(function(data) {
			    console.log(data);
			    Materialize.toast(data, 4000);
			});
		console.log("hello again");
		    });
    }
    else {
	$.post("/api/updateinfo", {
		"gymId": document.getElementById("gymId").value,
		"type": id,
		"text": JSON.stringify(updateValue)
	    },
	    "json")
	.done(function(data) {
		console.log(data);
		Materialize.toast(data, 4000);
	    })
    }
};
var addImage = function() {
    var imgLength = document.getElementsByClassName("inputImg").length + 1;
    var node = document.createElement("input");
    node.type = "file";
    node.className = "inputImg";
    node.name = "pic" + imgLength;
    node.accept = "image/*";
    document.getElementById("inputImgs").appendChild(node);
}
var addTime = function() {
    var timeLength = document.getElementsByClassName("time").length + 1;
    var node = document.createElement("div");
    node.innerHTML = '<div class="input-group time" id=time' + timeLength + '>' +
    '<div class="input-group-addon">From </div>' +
    '<input type="time" name="from' + timeLength + '" class="form-control">' +
    '<div class="input-group-addon"> to </div>' +
    '<input type="time" name="to' + timeLength + '" class="form-control">' +
    '<div class="input-group-addon">on</div>' +
    '<select class="form-control" name="day' + timeLength + '">' +
    '<option>Everyday</option>' +
    '<option>Weekdays</option>' +
    '<option>Weekends</option>' +
    '<option>Monday</option>' +
    '<option>Tuesday</option>' +
    '<option>Wednesday</option>' +
    '<option>Thursday</option>' +
    '<option>Friday</option>' +
    '<option>Saturday</option>' +
    '<option>Sunday</option>' +
    '</select>' +
    '<div onclick="removeTime(this.parentElement.id)" class="input-group-addon btn-default" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></div>' +
    '</div>';
    document.getElementById("time").appendChild(node);
};
var removeImage = function(id) {
    console.log(id);
    $.post("/removeImages", {
	    "gymId": document.getElementById("gymId").value,
		"imgName": id,
		},
	"json")
    .done(function(data) {
	    console.log(data);
	    Materialize.toast(data);
	    if (data=="Image removal successful!") {
		$("#"+id.replace('.', '')).hide();
	    }
	})
};
var removeTime = function(id) {
    console.log(id);
    $("#" + id).remove();
    for (var i=0; i<document.getElementsByClassName("time").length; i++) {
	document.getElementsByClassName("time")[i].children[1].name = "from" + (i+1);
	document.getElementsByClassName("time")[i].children[3].name = "to" + (i+1);
	document.getElementsByClassName("time")[i].children[5].name = "day" + (i+1);
	document.getElementsByClassName("time")[i].id = "time" + (i+1);
    }
};
var expand = function(days, doc) {
    console.log(doc);
    $(doc).remove();
    newInnerHTML = "";
    if (days=="Weekends") {
	daysList = ["Saturday", "Sunday"];
    }
    else if (days=="Weekdays") {
	daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    }
    else if (days=="Everyday") {
	daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    }
    for (var i=0; i<daysList.length; i++) {
 	newInnerHTML = newInnerHTML + '<div class="input-group time">' + document.getElementById("expand"+days).innerHTML.replace(days, daysList[i]) + "</div>";
    }
    document.getElementById("time").innerHTML = newInnerHTML;
    for (var i=0; i<daysList.length; i++) {
	$("."+daysList[i]).val(daysList[i]);
    }
    updateNameIndexes();
    
};
var updateNameIndexes = function() {
    var timeIndex = 1;
    $(".hours-info-from").each(function() {
	    this.name="from"+timeIndex;
	    timeIndex = timeIndex+1;
	});
    timeIndex = 1;
    $(".hours-info-to").each(function() {
	    this.name="to"+timeIndex;
	    timeIndex = timeIndex+1;
	});
    timeIndex = 1;
    $(".hours-info-day").each(function() {
	    this.name="day"+timeIndex;
	    timeIndex = timeIndex+1;
	});
};
updateNameIndexes();