L.mapbox.accessToken = 'pk.eyJ1IjoicGluZ3ltcyIsImEiOiJhYjI3YjAwZDU1YmRhMmZlYjljOGYxODNmMjIyYzU2MSJ9.Ssr2xrhyhlIpnSr5rQRFvQ';
var map = L.mapbox.map('map', 'mapbox.comic');
var myLayer = L.mapbox.featureLayer().addTo(map);
var markers = [];
var availableMarkers = [];
if (!navigator.geolocation) {
    console.log('Geolocation is not available');
} else {
    map.locate();
}

// Once we've got a position, zoom and center the map
// on it, and add a single marker.
map.on('locationfound', function(e) {
	//map.fitBounds([[e.bounds._southWest.lat-.03, e.bounds._southWest.lng-.03], [e.bounds._northEast.lat+.03, e.bounds._northEast.lng+.03]]);
	//myLocation = e.latlng.lat + "," + e.latlng.lng;
	map.fitBounds([[40.712895, -73.852834], [40.772895, -73.912834]])
	myLocation = "40.742895,-73.882834";
	//console.log('found');
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
  '&query=CLIENT_QUERY' +
  '&callback=?';
var foursquarePlaces = L.layerGroup().addTo(map);
//var foursquarePlaces = L.mapbox.featureLayer().addTo(map);
//foursquarePlaces.on("click", function(e) {
//	console.log("clicked");
//    });
//console.log('api');
var bsvar;
var resetColors = function() {
    for (var i=0; i<availableMarkers.length; i++) {
	availableMarkers[i].setIcon(L.mapbox.marker.icon({
		    'marker-color': '#BE9A6B',
		    'marker-symbol': '',
		    'marker-size': 'large'
		})
	    )
    }
}
map.on("click", resetColors);
var searchGyms = function() {
    var query = document.getElementById("search").value;
    clearMarkers();
    $.getJSON(API_ENDPOINT
	      .replace('CLIENT_ID', CLIENT_ID)
	      .replace('CLIENT_SECRET', CLIENT_SECRET)
	      .replace('LATLON', myLocation)
	      .replace('CLIENT_QUERY', query), function(result, status) {
		  if (status !== 'success') return alert('Request to Foursquare failed');
		  for (var i = 0; i < result.response.venues.length; i++) {
		      var venue = result.response.venues[i];
		      var latlng = L.latLng(venue.location.lat, venue.location.lng);
		      var markerColor;
		      var venueName;
		      var inputValues;
		      if (takenGyms.indexOf(venue.id) > -1) {
			  markerColor = "#ff8888";
			  venueName = venue.name + " (already registered)";
			  inputValues = "";
		      }
		      else {
			  markerColor = "#BE9A6B";
			  venueName = venue.name;
			  inputValues = '<input type="hidden" name="gymId" value="' + venue.id + '">' +
			      '<input type="hidden" name="gymName" value="' + venue.name + '">' +
			      '<input type="hidden" name="gymLat" value="' + venue.location.lat + '">' +
			      '<input type="hidden" name="gymLng" value="' + venue.location.lng + '">' +
			      '<input type="hidden" name="gymAddress" value="' + venue.location.address + '">';
		      }
		      var marker = L.marker(latlng, {
			      icon: L.mapbox.marker.icon({
				      'marker-color': markerColor,
				      'marker-symbol': '',
				      'marker-size': 'large'
				  })
			  })
			  .bindPopup('<strong><a href="https://foursquare.com/v/' + venue.id + '">' +
				     venueName + '</a></strong>' + inputValues)
			  .addTo(foursquarePlaces);
		      markers.push(marker);
		      if (takenGyms.indexOf(venue.id) < 0) {
			  //console.log("not taken");
			  marker.on("click", function() {
				      //console.log("hi");
				      bsvar = this;
				      resetColors();
				      this.setIcon(L.mapbox.marker.icon({
						  'marker-color': '#BE9A6B',
						      'marker-size': 'large',
						      'marker-symbol': 'star'
						      })
					  );
				  });
			  availableMarkers.push(marker);
		      }
		  }
	      })
};

var checkSubmissions = function() {
    if (document.forms['gymInformation']['gymType'].value === '' || document.forms['gymInformation']['priceValue1'].value === '' || document.forms['gymInformation']['to1'].value === '' || document.forms['gymInformation']['from1'].value === '') {
	Materialize.toast("Please fill out the required fields", 4000);
	return false;
    }
};

var clearMarkers = function() {
    //console.log(markers);
    for (var i=0; i<markers.length; i++) {
	map.removeLayer(markers[i]);
    }
    markers = [];
};