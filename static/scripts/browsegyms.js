$(function()
{
	$('.scroll-pane').each(
		function()
		{
			$(this).jScrollPane(
				{
					showArrows: $(this).is('.arrow')
				}
			);
			var api = $(this).data('jsp');
			var throttleTimeout;
			$(window).bind(
				'resize',
				function()
				{
					// IE fires multiple resize events while you are dragging the browser window which
					// causes it to crash if you try to update the scrollpane on every one. So we need
					// to throttle it to fire a maximum of once every 50 milliseconds...
					if (!throttleTimeout) {
						throttleTimeout = setTimeout(
							function()
							{
								api.reinitialise();
								throttleTimeout = null;
								console.log(api);
							},
							50
						);
					}
				}
			);
		}
	)

});
var jScrollPaneApi;
$(".div-hover").bind("click", function() {
	console.log(this.className);
	/*$('.scroll-pane').each(
			       function() {
			       $(this).data('jsp').reinitialise;
			       });*/
	if (this.className.indexOf("collapsed") == -1) {
	    console.log(this.style.backgroundColor="");
	}
	else {
	    console.log(this.style.backgroundColor="#C0C0C0");
	}
	setTimeout(function() {
		$('.scroll-pane').jScrollPane();
	    }, 
	    500);
    });
$("input[name='loc']").on("click", function() {
	console.log(myLocation);
	document.getElementById("myLoc").removeAttribute("disabled");
	document.getElementById("myLoc").value=myLocation;
    });
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
$(":checkbox").change(function() {
	var thisChecked = this.checked;
	$("input[name='" + this.name + "']").each(function() {
		this.checked = thisChecked;
	    });
    });
var disable = function(name) {
    $("." + name + "amount").attr("disabled", true);
}
var enable = function(name) {
    $("." + name + "amount").attr("disabled", false);
}
L.mapbox.accessToken = MAPBOX_ACCESS_TOKEN;
var map = L.mapbox.map('map', 'mapbox.light');
var myLayer = L.mapbox.featureLayer().addTo(map);
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
	console.log('found');
	myLayer.setGeoJSON({
		type: 'Feature',
		    geometry: {
		    type: 'Point',
			//coordinates: [e.latlng.lng, e.latlng.lat]
			coordinates: [40.742895, -73.882834]
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
    Materialize.toast('Position could not be found');
});
map.attributionControl
    .addAttribution('<a href="https://foursquare.com/">Places data from Foursquare</a>');

var API_ENDPOINT = 'https://api.foursquare.com/v2/venues/search' +
  '?client_id=CLIENT_ID' +
  '&client_secret=CLIENT_SECRET' +
  '&v=20130815' +
  '&ll=LATLON' +
  '&query=gym' +
  '&callback=?';
var MY_GYM = 'https://api.foursquare.com/v2/venues/GYM_ID';
var foursquarePlaces = L.layerGroup().addTo(map);
var databasePlaces = L.layerGroup().addTo(map);
var markPlaces = function() {
    console.log(gyms);
    if (showAll) {
	//mark foursquare places
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
			  .bindPopup('<strong><a href="/gym/' + venue.id + '">' +
				     venue.name +  '</a></strong>')
			  .addTo(foursquarePlaces);
		  }
		  markDatabasePlaces();
	      }
	      );
    }
    else {
	markDatabasePlaces();
    }
 };
var markDatabasePlaces = function() {
   //mark locations in database
    for (var i=0; i<gyms.length; i++) {
	var gym = gyms[i];
	var latlng = L.latLng(gym["lat"], gym["lng"]);
	var markerColor;
	if (showAll) {
	    markerColor = '#C0C0C0';
	}
	else {
	    var match = gym['match'];
	    if (match==0) {
		markerColor = '#00FF00';
	    }
	    else if (match<20) {
		markerColor = '#CCFF66';
	    }
	    else {
		markerColor = '#FFFF00';
	    }
	}
	var marker = L.marker(latlng, {
		icon: L.mapbox.marker.icon({
			'marker-color': markerColor,
			'marker-symbol': '',
			'marker-size': 'large'
		    })
	    })
	    //.bindPopup('<strong><a href="https://foursquare.com/v/' + gym['id'] + '">' +
	    .bindPopup('<strong><a href="/gym/' + gym['id'] + '">' +
		       gym['name'] + ' (verified gym)</a></strong>')
	.addTo(databasePlaces);
    }
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
    $('.scroll-pane').jScrollPane();
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
    $('.scroll-pane').jScrollPane();
};
//jScrollPane mousewheel
/**!
 * jQuery Mousewheel 3.1.12
 *
 * Copyright 2014 jQuery Foundation and other contributors
 * Released under the MIT license.
 * http://jquery.org/license
 */

(function (factory) {
    if ( typeof define === 'function' && define.amd ) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    } else if (typeof exports === 'object') {
        // Node/CommonJS style for Browserify
        module.exports = factory;
    } else {
        // Browser globals
        factory(jQuery);
    }
}(function ($) {

    var toFix  = ['wheel', 'mousewheel', 'DOMMouseScroll', 'MozMousePixelScroll'],
        toBind = ( 'onwheel' in document || document.documentMode >= 9 ) ?
                    ['wheel'] : ['mousewheel', 'DomMouseScroll', 'MozMousePixelScroll'],
        slice  = Array.prototype.slice,
        nullLowestDeltaTimeout, lowestDelta;

    if ( $.event.fixHooks ) {
        for ( var i = toFix.length; i; ) {
            $.event.fixHooks[ toFix[--i] ] = $.event.mouseHooks;
        }
    }

    var special = $.event.special.mousewheel = {
        version: '3.1.12',

        setup: function() {
            if ( this.addEventListener ) {
                for ( var i = toBind.length; i; ) {
                    this.addEventListener( toBind[--i], handler, false );
                }
            } else {
                this.onmousewheel = handler;
            }
            // Store the line height and page height for this particular element
            $.data(this, 'mousewheel-line-height', special.getLineHeight(this));
            $.data(this, 'mousewheel-page-height', special.getPageHeight(this));
        },

        teardown: function() {
            if ( this.removeEventListener ) {
                for ( var i = toBind.length; i; ) {
                    this.removeEventListener( toBind[--i], handler, false );
                }
            } else {
                this.onmousewheel = null;
            }
            // Clean up the data we added to the element
            $.removeData(this, 'mousewheel-line-height');
            $.removeData(this, 'mousewheel-page-height');
        },

        getLineHeight: function(elem) {
            var $elem = $(elem),
                $parent = $elem['offsetParent' in $.fn ? 'offsetParent' : 'parent']();
            if (!$parent.length) {
                $parent = $('body');
            }
            return parseInt($parent.css('fontSize'), 10) || parseInt($elem.css('fontSize'), 10) || 16;
        },

        getPageHeight: function(elem) {
            return $(elem).height();
        },

        settings: {
            adjustOldDeltas: true, // see shouldAdjustOldDeltas() below
            normalizeOffset: true  // calls getBoundingClientRect for each event
        }
    };

    $.fn.extend({
        mousewheel: function(fn) {
            return fn ? this.bind('mousewheel', fn) : this.trigger('mousewheel');
        },

        unmousewheel: function(fn) {
            return this.unbind('mousewheel', fn);
        }
    });


    function handler(event) {
        var orgEvent   = event || window.event,
            args       = slice.call(arguments, 1),
            delta      = 0,
            deltaX     = 0,
            deltaY     = 0,
            absDelta   = 0,
            offsetX    = 0,
            offsetY    = 0;
        event = $.event.fix(orgEvent);
        event.type = 'mousewheel';

        // Old school scrollwheel delta
        if ( 'detail'      in orgEvent ) { deltaY = orgEvent.detail * -1;      }
        if ( 'wheelDelta'  in orgEvent ) { deltaY = orgEvent.wheelDelta;       }
        if ( 'wheelDeltaY' in orgEvent ) { deltaY = orgEvent.wheelDeltaY;      }
        if ( 'wheelDeltaX' in orgEvent ) { deltaX = orgEvent.wheelDeltaX * -1; }

        // Firefox < 17 horizontal scrolling related to DOMMouseScroll event
        if ( 'axis' in orgEvent && orgEvent.axis === orgEvent.HORIZONTAL_AXIS ) {
            deltaX = deltaY * -1;
            deltaY = 0;
        }

        // Set delta to be deltaY or deltaX if deltaY is 0 for backwards compatabilitiy
        delta = deltaY === 0 ? deltaX : deltaY;

        // New school wheel delta (wheel event)
        if ( 'deltaY' in orgEvent ) {
            deltaY = orgEvent.deltaY * -1;
            delta  = deltaY;
        }
        if ( 'deltaX' in orgEvent ) {
            deltaX = orgEvent.deltaX;
            if ( deltaY === 0 ) { delta  = deltaX * -1; }
        }

        // No change actually happened, no reason to go any further
        if ( deltaY === 0 && deltaX === 0 ) { return; }

        // Need to convert lines and pages to pixels if we aren't already in pixels
        // There are three delta modes:
        //   * deltaMode 0 is by pixels, nothing to do
        //   * deltaMode 1 is by lines
        //   * deltaMode 2 is by pages
        if ( orgEvent.deltaMode === 1 ) {
            var lineHeight = $.data(this, 'mousewheel-line-height');
            delta  *= lineHeight;
            deltaY *= lineHeight;
            deltaX *= lineHeight;
        } else if ( orgEvent.deltaMode === 2 ) {
            var pageHeight = $.data(this, 'mousewheel-page-height');
            delta  *= pageHeight;
            deltaY *= pageHeight;
            deltaX *= pageHeight;
        }

        // Store lowest absolute delta to normalize the delta values
        absDelta = Math.max( Math.abs(deltaY), Math.abs(deltaX) );

        if ( !lowestDelta || absDelta < lowestDelta ) {
            lowestDelta = absDelta;

            // Adjust older deltas if necessary
            if ( shouldAdjustOldDeltas(orgEvent, absDelta) ) {
                lowestDelta /= 40;
            }
        }

        // Adjust older deltas if necessary
        if ( shouldAdjustOldDeltas(orgEvent, absDelta) ) {
            // Divide all the things by 40!
            delta  /= 40;
            deltaX /= 40;
            deltaY /= 40;
        }

        // Get a whole, normalized value for the deltas
        delta  = Math[ delta  >= 1 ? 'floor' : 'ceil' ](delta  / lowestDelta);
        deltaX = Math[ deltaX >= 1 ? 'floor' : 'ceil' ](deltaX / lowestDelta);
        deltaY = Math[ deltaY >= 1 ? 'floor' : 'ceil' ](deltaY / lowestDelta);

        // Normalise offsetX and offsetY properties
        if ( special.settings.normalizeOffset && this.getBoundingClientRect ) {
            var boundingRect = this.getBoundingClientRect();
            offsetX = event.clientX - boundingRect.left;
            offsetY = event.clientY - boundingRect.top;
        }

        // Add information to the event object
        event.deltaX = deltaX;
        event.deltaY = deltaY;
        event.deltaFactor = lowestDelta;
        event.offsetX = offsetX;
        event.offsetY = offsetY;
        // Go ahead and set deltaMode to 0 since we converted to pixels
        // Although this is a little odd since we overwrite the deltaX/Y
        // properties with normalized deltas.
        event.deltaMode = 0;

        // Add event and delta to the front of the arguments
        args.unshift(event, delta, deltaX, deltaY);

        // Clearout lowestDelta after sometime to better
        // handle multiple device types that give different
        // a different lowestDelta
        // Ex: trackpad = 3 and mouse wheel = 120
        if (nullLowestDeltaTimeout) { clearTimeout(nullLowestDeltaTimeout); }
        nullLowestDeltaTimeout = setTimeout(nullLowestDelta, 200);

        return ($.event.dispatch || $.event.handle).apply(this, args);
    }

    function nullLowestDelta() {
        lowestDelta = null;
    }

    function shouldAdjustOldDeltas(orgEvent, absDelta) {
        // If this is an older event and the delta is divisable by 120,
        // then we are assuming that the browser is treating this as an
        // older mouse wheel event and that we should divide the deltas
        // by 40 to try and get a more usable deltaFactor.
        // Side note, this actually impacts the reported scroll distance
        // in older browsers and can cause scrolling to be slower than native.
        // Turn this off by setting $.event.special.mousewheel.settings.adjustOldDeltas to false.
        return special.settings.adjustOldDeltas && orgEvent.type === 'mousewheel' && absDelta % 120 === 0;
    }

}));
