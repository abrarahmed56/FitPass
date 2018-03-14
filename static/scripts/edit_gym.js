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
	var $equipmentinfo = $(".equipment");
	//console.log($equipmentinfo);
	
	var updateValue = {};
	console.log($equipmentinfo);
	//for (var i=0; i<$updateValue.length; i++) {
	$equipmentinfo.each(function() {
		console.log("this: " + this);
		updateValue[this.children[1].value] = this.children[3].value;
	    });
    }
    else if (id==="Hours") {
	var $hoursinfo = $("#hours input, #hours select");
	var updateValue = {};
	console.log($hoursinfo);
	$hoursinfo.each(function() {
		updateValue[this.name] = $(this).val();
	    });
	    console.log("updateValue dict:");
	console.log(updateValue);
    }
    else if (id==="Price") {
	//var $prices = $("#prices input, #prices select");
	var $prices = $(".price");
	console.log($prices);
	//var updateValue = {};
	var updateValue = []
	var index = 0;
	$prices.each(function() {
		//updateValue[this.name] = $(this).val();
		console.log(this);
		updateValue.push([this.children[1].value, 
				  this.children[3].value, 
				  this.children[5].value]);
		index = index + 3
	    });
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
};
var addPrice = function() {
    var priceLength = document.getElementsByClassName("price").length + 1;
    var node = document.createElement("div");
    node.innerHTML = '<div class="input-group price" id="price' + priceLength + '">' +
    '<div class="input-group-addon">$</div><input class="form-control" name="priceValue' + priceLength + '" type="number">' +
    '<div class="input-group-addon">per</div>' +
    '<select class="form-control" name="priceUnit' + priceLength + '">' +
    '<option>month</option>' +
    '<option>year</option>' +
    '<option>class</option>' +
    '</select>' +
    '<div class="input-group-addon">for</div><input class="form-control" name="priceTarget1" placeholder="ie, students, seniors, group, etc.">' +
    '<div onclick="removeRow(this.parentElement.id, &#34;price&#34;)" class="input-group-addon btn-default" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></div></div>';
    document.getElementById("prices").appendChild(node);
};
var addEquipment = function() {
    var equipmentLength = document.getElementsByClassName("equipment").length + 1;
    var node = document.createElement("div");
    node.innerHTML = '<div class="input-group equipment" id="equipment' + equipmentLength + '">' +
    '<div class="input-group-addon">Equipment</div>' +
    '<input list="equipments" class="form-control" name="equipmentName' + equipmentLength + '">' +
    '<div class="input-group-addon">Amount</div>' +
    '<input class="form-control" type="number" name="equipmentAmount' + equipmentLength + '">' +
    '<div onclick="removeRow(this.parentElement.id, &#34;equipment&#34;)" class="input-group-addon btn-default" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></div>';
    document.getElementById("equipment").appendChild(node);
};
var addTime = function() {
    var timeLength = document.getElementsByClassName("time").length + 1;
    var node = document.createElement("div");
    node.innerHTML = '<div class="input-group time" id="time' + timeLength + '">' +
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
    '<div onclick="convertToInputHoursSpecific(this, this.parentNode, ' + timeLength + ')" class="input-group-addon">Click here if these hours are for a specific part of the gym<div></div></div>' +
    '<div onclick="removeRow(this.parentElement.id, &#34;time&#34;)" class="input-group-addon btn-default" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></div>' +
    '</div>';
    document.getElementById("time").appendChild(node);
};
var convertToInputHoursSpecific = function(el, parent, num) {
    el.innerHTML = "for";
    var node = document.createElement("input");
    node.type = "text";
    node.className = "form-control";
    node.name = "gymPart" + num;
    console.log(parent.childNodes[parent.childNodes.length-2]);
    console.log($(parent).children()[0]);
    console.log($(parent).children()[$(parent).children().length-1]);
    parent.insertBefore(node, $(parent).children()[$(parent).children().length-1]);
    el.onclick = "";
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
var removeExpand = function(id) {
    document.getElementById(id).remove();
};
var removeRow = function(id, className) {
    console.log(id);
    console.log(className);
    $("#" + id).remove();
    if (className.substring(0, 4)==="time") {
	for (var i=0; i<document.getElementsByClassName(className).length; i++) {
	    document.getElementsByClassName(className)[i].children[1].name = "from" + (i+1);
	    document.getElementsByClassName(className)[i].children[3].name = "to" + (i+1);
	    document.getElementsByClassName(className)[i].children[5].name = "day" + (i+1);
	    document.getElementsByClassName(className)[i].id = className + (i+1);
	}
    }
    else if (className==="price") {
	for (var i=0; i<document.getElementsByClassName(className).length; i++) {
	    document.getElementsByClassName(className)[i].children[1].id = "priceValue" + (i+1);
	    document.getElementsByClassName(className)[i].children[3].id = "priceTarget" + (i+1);
	    document.getElementsByClassName(className)[i].id = className + (i+1);
	}
    }
    else if (className==="equipment") {
	for (var i=0; i<document.getElementsByClassName(className).length; i++) {
	    document.getElementsByClassName(className)[i].children[1].id = "equipmentName" + (i+1);
	    document.getElementsByClassName(className)[i].children[1].id = "equipmentAmount" + (i+1);
	    document.getElementsByClassName(className)[i].id = className + (i+1);
	}
    }
};
var expand = function(days, doc) {
    console.log(doc);
    $(doc).remove();
    newNode = document.createElement('div');
    //newNode.className="input-group time"
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
	//subNode = document.createElement
 	newNode.innerHTML += '<div class="input-group time">' + document.getElementById("expand"+days).innerHTML.replace(days, daysList[i]) + "</div>";
    }
    //document.getElementById("expand"+days).innerHTML = newInnerHTML;
    document.getElementById("time").replaceChild(newNode, document.getElementById("expand"+days));
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