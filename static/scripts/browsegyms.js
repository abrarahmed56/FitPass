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
var getDirections = function(destination) {
    console.log("getdirections");
    document.getElementById("map-canvas").innerHTML = '<iframe width="600" height="450" frameborder="0" style="border:0" src="https://www.google.com/maps/embed/v1/directions?origin=' + myLatlng + '&destination=' + destination + '&key=AIzaSyDdo_KgLSto4lQuQqThUFT5r2d8uU4-TdQ"</iframe>';
};
var showGyms = function() {
    console.log("show");
    //console.log(gyms);
    var request = {
	location: myLatlng,
	radius: 10000,
	keyword: 'gym',
	//types: ['gym']
    };
    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch(request, callback);
    $.post("/api/getallgyms")
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
	});
}
var filter = function() {
    console.log("filter");
    var keyword = ""
    if (document.getElementById("weighttraining").checked) {
	keyword = keyword + "weight training ";
    }
    if (document.getElementById("endurance").checked) {
	keyword = keyword + "endurance ";
    }
    if (document.getElementById("yoga").checked) {
	keyword = keyword + "yoga pilates ";
    }
    console.log(keyword);
    var request = {
	location: myLatlng,
	radius: 10000,
	keyword: 'gym',
	//types: ['gym']
    };
    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch(request, callback);
};
//TODO: use gymflow api for gym traffic
var callback = function(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
	for (var i = 0; i < results.length; i++) {
	    createMarker(results[i]);
	}
    }
}
var callback2 = function(place, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
	createMarker(place);
    }
}
var createMarker = function(place) {
    var placeLoc = place.geometry.location;
    var marker = new google.maps.Marker({
	map: map,
	position: place.geometry.location
    });
    google.maps.event.addListener(marker, 'click', function() {
	infowindow.setContent("<div style='color:black'>Loading</div>");
	var request = {placeId: place.place_id};
	var service = new google.maps.places.PlacesService(map);
	service.getDetails(request, function(place, status) {
	    if (status == google.maps.places.PlacesServiceStatus.OK) {
		$.post("/api/getDetails", {"url": "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + place.place_id + "&key=AIzaSyCEx5q1pE1dPVNR7GwjWfCGSRHteZIgieY",
					   "id": place.place_id})
		    .done(function(jsondata) {
			console.log(jsondata);
			data = JSON.parse(jsondata);
			infowindow.setContent("<div style='color:black'><b>" + place.name + "</b>" + "<br>Website: " + data['website'] + "<br>Phone: " + data['phone'] + "</div>");
			document.getElementById("gymInfo").innerHTML = "<h1>" + place.name + "</h1><h2>Equipment:</h2>" + data['equipment'] + "<h2>Requirements:</h2>" + data['requirements'] + "<h2>Miscellaneous/Extras:</h2>" + data['misc'] + "<br><button onclick='getDirections(&quot;" + place.formatted_address + "&quot;)'>Directions</button>";
		    })
	    }
	});
	infowindow.open(map, this);
	//infowindow.setContent(place.name);
    });
}
$(".scroll-pane").attr("height", "500px");
