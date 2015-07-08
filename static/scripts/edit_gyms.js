var myLatlng;
var infowindow;
var map;
var markers = [];
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
	myLatlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
	var mapOptions = {
	    zoom:15,
	    center: myLatlng
	};
	map = new google.maps.Map($("#map-canvas")[0], mapOptions);
	infowindow = new google.maps.InfoWindow();
    });
};
var showGyms = function() {
    var request1 = {
	location: myLatlng,
	keyword: 'gym',
	//types: ['gym']
    };
    var request2 = {
	location: myLatlng,
	radius: 10000,
	keyword: gymName,
	//types: ['gym']
    };
    var service = new google.maps.places.PlacesService(map);
    //service.nearbySearch(request1, callback);
    service.nearbySearch(request2, callback);
}
var callback = function(results, status) {
    for (var i = 0; i < markers.length; i++) {
	markers[i].setMap(null);
    }
    if (status == google.maps.places.PlacesServiceStatus.OK) {
	for (var i = 0; i < results.length; i++) {
	    createMarker(results[i]);
	}
    }
}
var createMarker = function(place) {
    var placeLoc = place.geometry.location;
    var marker = new google.maps.Marker({
	map: map,
	position: place.geometry.location
    });
    markers.push(marker);
    google.maps.event.addListener(marker, 'click', function() {
	infowindow.setContent("<div style='color:black'>Loading</div>");
	var request = {placeId: place.place_id};
	var service = new google.maps.places.PlacesService(map);
	service.getDetails(request, function(place, status) {
	    if (status == google.maps.places.PlacesServiceStatus.OK) {
		$.post("/api/getDetails", {"url": "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + place.place_id + "&key=AIzaSyCEx5q1pE1dPVNR7GwjWfCGSRHteZIgieY",
					   "x": marker['position']['A'],
					   "y": marker['position']['F']
})
		    .done(function(jsondata) {
			data = JSON.parse(jsondata);
			infowindow.setContent("<div style='color:black'><b>" + place.name + "</b>" + "<br>Website: <a href='" + data['website'] + "'>" + data['website'] + "</a><br>Phone: " + data['phone'] + "<br>" + data['button'] + "</div><input type='hidden' id='x' value=" + marker['position']['A'] + "><input type='hidden' id='y' value=" + marker['position']['F'] + ">");
			document.getElementById("editamenities").innerHTML = "<h2>Amenities:</h2><br>Equipment:<input id='equipment' type='text'><button onclick='updateInfo(&quot;equipment&quot;)'>Update</button><br>Requirements:<input id='requirements' type='text'><button onclick='updateInfo(&quot;requirements&quot;)'>Update</button><br>Misc/Extras:<input id='misc' type='text'><button onclick='updateInfo(&quot;misc&quot;)'>Update</button>"
		    })
	    }
	});
	infowindow.open(map, this);
    });
}
var updateInfo = function(id) {
    var updateValue = document.getElementById(id).value
}
var search = function() {
    var query = document.getElementById("search").value;
    var request = {
	location: myLatlng,
	radius: 10000,
	keyword: query,
	//types: ['gym']
    };
    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch(request, callback);
}
var addGym = function() {
    $.post("/api/addgym", {"x": document.getElementById("x").value,
			   "y": document.getElementById("y").value
    })
	.done(function(data) {
	    console.log(data);
	    if (data==="Gym added!") {
		document.getElementById("markerbutton").innerHTML = "Remove from your Gyms";
		document.getElementById("markerbutton").onclick = removeGym;
	    }
	});
}
var removeGym = function() {
    $.post("/api/removegym", {"x": document.getElementById("x").value,
			      "y": document.getElementById("y").value
    })
	.done(function(data) {
	    console.log(data);
	    if (data==="Gym deleted!") {
		document.getElementById("markerbutton").innerHTML = "Add to your Gyms";
		document.getElementById("markerbutton").onclick = addGym;
	    }
	    else {
		console.log("HI");
	    }
 	});
}
