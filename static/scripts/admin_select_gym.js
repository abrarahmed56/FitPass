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
	map.fitBounds([[40.712895, -73.852834], [40.772895, -73.912834]]);
	//myLocation = e.latlng.lat + "," + e.latlng.lng;
	myLocation = "40.742895,-73.882834";
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
//var foursquarePlaces = L.layerGroup().addTo(map);
var foursquarePlaces = L.mapbox.featureLayer().addTo(map);
//foursquarePlaces.on("click", function(e) {
//	console.log("clicked");
//    });
console.log('api');
var bsvar;
var resetColors = function() {
    for (var i=0; i<availableMarkers.length; i++) {
	//if (takenGyms.indexOf(venue.id) < 0) {
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
			  inputValues = '<input type="hidden" id="gymId" value="' + venue.id + '">';
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
		      //display properties onclick or onbuttonpress
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
			  console.log("not taken");
			  marker.on("click", function() {
				      console.log("hi");
				      resetColors();
				      this.setIcon(L.mapbox.marker.icon({
						  'marker-color': '#ff8888',
						  'marker-size': 'large',
						  'marker-symbol': 'star'
						      })
					  );
				      console.log("No info available");
				      document.getElementById("Price").value = "";
				      document.getElementById("PriceUnit").value = "month";
				      //document.getElementById("type")
				      $("input[value='" + gymInfo['type'] + "']")[0].checked="checked";
				      document.getElementById("Requirements").value = "";
				      document.getElementById("Misc").value = "";
				      document.getElementById("hours");
				      resetHours();
				      //parse through equipment and other info, enter into form				  });
			  availableMarkers.push(marker);
			      });
		      }
		      else {
			  console.log("taken");
			  marker.on("click", function() {
				      console.log("hi");
				      resetColors();
				      var bsvar = this;
				      this.setIcon(L.mapbox.marker.icon({
						  //'marker-color': '#BE9A6B',
						  'marker-size': 'large',
						  'marker-symbol': 'star'
						      })
					  );
				      $.post('/api/getgyminfo',
					     {
						 'gymId': document.getElementById("gymId").value
					     },
					     function(data) {
					      console.log(data);
					      gymInfo = JSON.parse(data);
					      gymEquipment = gymInfo['equipment'];
					      for (var i=0; i<gymEquipment.length-4; i++) {
						  var equipmentNum = document.getElementsByClassName("equipment")[i];
						  var equipmentCheckbox = document.getElementsByClassName("equipmentcheckbox")[i];
						  if (gymEquipment[i] <= 0) {
						      equipmentCheckbox.checked="";
						      equipmentNum.disabled = "disabled";
						  }
						  else {
						      equipmentCheckbox.checked="checked";
						      equipmentNum.disabled = "";
						  }
						  document.getElementsByClassName("equipment")[i].value = gymEquipment[i];
					      }
					      document.getElementById("Price").value = gymInfo['price'].split(":")[0];
					      document.getElementById("PriceUnit").value = gymInfo['price'].split(":")[1];
					      //document.getElementById("type")
					      $("input[value='" + gymInfo['type'] + "']")[0].checked="checked";
					      document.getElementById("Requirements").value = gymInfo['requirements'];
					      document.getElementById("Misc").value = gymInfo['misc'];
					      document.getElementById("hours");
					      console.log(gymInfo['hours']);
					      displayHours(gymInfo['hours']);
					      //parse through equipment and other info, enter into form
					     });
			      });
			  availableMarkers.push(marker);
		      }
		  }
	      }
	      )
};	      

var clearMarkers = function() {
    console.log(markers);
    for (var i=0; i<markers.length; i++) {
	map.removeLayer(markers[i]);
    }
    markers = [];
};

var resetHours = function() {
    var node = document.createElement("div");
    node.innerHTML = '<div class="input-group time" id=time1>' +
    '<div class="input-group-addon">From </div>' +
    '<input type="time" name="from1" class="form-control">' +
    '<div class="input-group-addon"> to </div>' +
    '<input type="time" name="to1" class="form-control">' +
    '<div class="input-group-addon">on</div>' +
    '<select class="form-control" name="day1">' +
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
    document.getElementById("time").innerHTML = "";
    document.getElementById("time").appendChild(node);
}

var displayHours = function(hours) {
    document.getElementById("time").innerHTML = "";
    for (key in hours) {
	console.log(key);
	console.log(hours[key]);
	console.log('hours');
	for (var i=0; i<hours[key].length; i++) {
	    console.log(hours[key][i]);
	    //TODO USE FUNCTION ADDTIME INSTEAD OF HARD CODING IT
	    var timeLength = document.getElementsByClassName("time").length + 1;
	    var node = document.createElement("div");
	    node.innerHTML = '<div class="input-group time" id=time' + timeLength + '>' +
		'<div class="input-group-addon">From </div>' +
		'<input type="time" name="from' + timeLength + '" class="form-control" value="' + hours[key][i][0] + '">' +
		'<div class="input-group-addon"> to </div>' +
		'<input type="time" name="to' + timeLength + '" class="form-control" value="' + hours[key][i][1] + '">' +
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
	}
    }
}