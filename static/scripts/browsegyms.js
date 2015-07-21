var myLocation;
$(":radio").change(function() {
	$.map($("." + this.className.split(" ")[0]), function(that) {
		console.log(that.value);
		disable(that.value);
	    });
	enable(this.value);
    });
var clearSelection = function(className) {
    $.map($("."+className), function(that) {
	    that.checked = false;
	    if ($(that).hasClass(className+"input")) {
		disable(that.value);
	    }
	});
};
var disable = function(name) {
    //document.getElementsByClassName(name + "amount").setAttribute("disabled", true);
    $("." + name + "amount").attr("disabled", true);
}
var enable = function(name) {
    //document.getElementsByClassName(name + "amount").setAttribute("disabled", false);
    $("." + name + "amount").attr("disabled", false);
}
$(".scroll-pane").attr("height", "500px");
L.mapbox.accessToken = 'pk.eyJ1IjoicGluZ3ltcyIsImEiOiJhYjI3YjAwZDU1YmRhMmZlYjljOGYxODNmMjIyYzU2MSJ9.Ssr2xrhyhlIpnSr5rQRFvQ';
var map = L.mapbox.map('map', 'mapbox.comic');
var myLayer = L.mapbox.featureLayer().addTo(map);
if (!navigator.geolocation) {
    console.log('Geolocation is not available');
} else {
    map.locate();
}

// Once we've got a position, zoom and center the map
// on it, and add a single marker.
map.on('locationfound', function(e) {
	map.fitBounds([[e.bounds._southWest.lat-.03, e.bounds._southWest.lng-.03], [e.bounds._northEast.lat+.03, e.bounds._northEast.lng+.03]]);
	myLocation = e.latlng.lat + "," + e.latlng.lng;
	console.log('found');
	myLayer.setGeoJSON({
		type: 'Feature',
		    geometry: {
		    type: 'Point',
			coordinates: [e.latlng.lng, e.latlng.lat]
			},
		    properties: {
		    'title': 'Here I am!',
			'marker-color': '#ff8888',
			'marker-symbol': 'star'
			}
	    });
	markPlaces();
});

// If the user chooses not to allow their location
// to be shared, display an error message.
map.on('locationerror', function() {
    console.log('Position could not be found');
});
map.attributionControl
    .addAttribution('<a href="https://foursquare.com/">Places data from Foursquare</a>');

var CLIENT_ID = 'L4UK14EMS0MCEZOVVUYX2UO5ULFHJN3EHOFVQFSW0Z1MSFSR';
var CLIENT_SECRET = 'YKJB0JRFDPPSGTHALFOEP5O1NDDATHKQ2IZ5RO2GOX452SFA';
var API_ENDPOINT = 'https://api.foursquare.com/v2/venues/search' +
  '?client_id=CLIENT_ID' +
  '&client_secret=CLIENT_SECRET' +
  '&v=20130815' +
  '&ll=LATLON' +
  '&query=gym' +
  '&callback=?';
var MY_GYM = 'https://api.foursquare.com/v2/venues/GYM_ID';
var foursquarePlaces = L.layerGroup().addTo(map);
console.log('api');
var markPlaces = function() {
    if (showAll) {
    $.getJSON(API_ENDPOINT
	      .replace('CLIENT_ID', CLIENT_ID)
	      .replace('CLIENT_SECRET', CLIENT_SECRET)
	      .replace('LATLON', myLocation), function(result, status) {
	      //.replace('LATLON', myLayer.getGeoJSON().geometry.coordinates[1] + ',' + myLayer.getGeoJSON().geometry.coordinates[0]), function(result, status) {
		  if (status !== 'success') return alert('Request to Foursquare failed');
		  for (var i = 0; i < result.response.venues.length; i++) {
		      var venue = result.response.venues[i];
		      var latlng = L.latLng(venue.location.lat, venue.location.lng);
		      var marker = L.marker(latlng, {
			      icon: L.mapbox.marker.icon({
				      'marker-color': '#BE9A6B',
				      'marker-symbol': '',
				      'marker-size': 'large'
				  })
			  })
			  .bindPopup('<strong><a href="https://foursquare.com/v/' + venue.id + '">' +
				     venue.name + '</a></strong>')
			  .addTo(foursquarePlaces);
			  }
	      }
	      );
    }
    console.log(gyms);
    for (var i=0; i<gyms.length; i++) {
	var gym = gyms[i];
	console.log(gym);
	var latlng = L.latLng(gym["lat"], gym["lng"]);
	var marker = L.marker(latlng, {
		icon: L.mapbox.marker.icon({
			'marker-color': '#C0C0C0',
			'marker-symbol': '',
			'marker-size': 'large'
		    })
	    })
	    //.bindPopup('<strong><a href="https://foursquare.com/v/' + gym['id'] + '">' +
	    .bindPopup('<strong><a href="/gym/' + gym['id'] + '">' +
		       gym['name'] + ' (verified gym)</a></strong>')
	    .addTo(foursquarePlaces);
    }
    /*$.getJSON(MY_GYM
	      .replace('GYM_ID', gymId)

	      );*/
};
