var myLatlng;
var infowindow;
var map;
var data;
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
	myLatlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
	var mapOptions = {
	    zoom:15,
	    center: myLatlng
	};
	map = new google.maps.Map($("#map-canvas")[0], mapOptions);
	infowindow = new google.maps.InfoWindow();
	showGyms()
    });
};
var showGyms = function() {
    console.log("show");
    var request1 = {
	location: myLatlng,
	radius: 1000,
	keyword: 'gym',
	//types: ['gym']
    };
    var request2 = {
	location: myLatlng,
	radius: 10000,
	keyword: 'blink fitness',
	//types: ['gym']
    };
    var service = new google.maps.places.PlacesService(map);
    //service.nearbySearch(request1, callback);
    service.nearbySearch(request2, callback);
}
var callback = function(results, status) {
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
    google.maps.event.addListener(marker, 'click', function() {
	infowindow.setContent("Loading");
	var request = {placeId: place.place_id};
	var service = new google.maps.places.PlacesService(map);
	service.getDetails(request, function(place, status) {
	    if (status == google.maps.places.PlacesServiceStatus.OK) {
		$.post("/api/getDetails", {"url": "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + place.place_id + "&key=AIzaSyCEx5q1pE1dPVNR7GwjWfCGSRHteZIgieY"})
		    .done(function(jsondata) {
			console.log(jsondata);
			data = JSON.parse(jsondata);
			infowindow.setContent("<b>" + place.name + "</b>" + "<br>Website: <a href='" + data['website'] + "'>" + data['website'] + "</a><br>Phone: " + data['phone']);
			document.getElementById("editamenities").innerHTML = "<h2>Amenities:</h2><br>Equipment:<input id='equipment' type='text'><button onclick='updateInfo(&quot;equipment&quot;)'>Update</button><br>Requirements:<input id='requirements' type='text'><button onclick='updateInfo(&quot;requirements&quot;)'>Update</button><br>Misc/Extras:<input id='misc' type='text'><button onclick='updateInfo(&quot;misc&quot;)'>Update</button>"
		    })
	    }
	});
	infowindow.open(map, this);
    });
}
var updateInfo = function(id) {
    var updateValue = document.getElementById(id).value
    console.log("updateValue: " + updateValue);
}
