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
    clearMarkers();
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
	console.log(place);
	service.getDetails(request, function(place, status) {
	    if (status == google.maps.places.PlacesServiceStatus.OK) {
		$.post("/api/getDetails", {"url": "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + place.place_id + "&key=AIzaSyCEx5q1pE1dPVNR7GwjWfCGSRHteZIgieY",
					   "id": place.place_id
})
		    .done(function(jsondata) {
			console.log(jsondata);
			data = JSON.parse(jsondata);
			infowindow.setContent("<div style='color:black'><b>" + place.name + "</b>" + "<br>Website: <a href='" + data['website'] + "'>" + data['website'] + "</a><br>Phone: " + data['phone'] + "<br>" + data['button'] + "</div><input type='hidden' id='x' value=" + marker['position']['A'] + "><input type='hidden' id='y' value=" + marker['position']['F'] + "><input type='hidden' id='placeId' value=" + place.place_id + ">");
			document.getElementById("editamenities").innerHTML = "<h2>Amenities:</h2><br>Equipment:<input id='Equipment' type='text' value='" + data['equipment'] + "'><button onclick='updateInfo(&quot;Equipment&quot;)'>Update</button><br>Requirements:<input id='Requirements' type='text' value='" + data['requirements'] + "'><button onclick='updateInfo(&quot;Requirements&quot;)'>Update</button><br>Misc/Extras:<input id='Misc' type='text' value='" + data['misc'] + "'><button onclick='updateInfo(&quot;Misc&quot;)'>Update</button>"
		    })
	    }
	});
	infowindow.open(map, this);
    });
}
var clearMarkers = function() {
    for (var i = 0; i < markers.length; i++) {
	markers[i].setMap(null);
    }
}
var updateInfo = function(id) {
    var updateValue = document.getElementById(id).value;
    $.post("/api/updateinfo", {
	"placeId": document.getElementById("placeId").value,
	"type": id,
	"text": document.getElementById(id).value
    })
	   .done(function(data) {
	       console.log(data);
	   })
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
			   "y": document.getElementById("y").value,
			   "id": document.getElementById("placeId").value
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
    $.post("/api/removegym", {"placeId": document.getElementById("placeId").value,
    })
	.done(function(data) {
	    console.log(data);
	    if (data==="Gym deleted!") {
		document.getElementById("markerbutton").innerHTML = "Add to your Gyms";
		document.getElementById("markerbutton").onclick = addGym;
	    }
 	});
}
var viewYourGyms = function() {
    clearMarkers();
    //TODO MAYBE- when gym removed, remove marker as well
    $.post("/api/getgyms")
	.done(function(jsondata) {
	    console.log(jsondata);
	    data = JSON.parse(jsondata);
	    for (var i=0; i<data.length; i++) {
		var request = {
		    placeId: data[i]
		}
		var service = new google.maps.places.PlacesService(map);
		service.getDetails(request, callback2);
	    }
	})
}
var callback2 = function(place, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
	createMarker(place);
    }
}
