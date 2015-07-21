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
var updateInfo = function(id) {
    if (id==="Equipment") {
	var $equipmentinfo = $("#equipment input[type='text']");
	var updateValue = {};
	//for (var i=0; i<$updateValue.length; i++) {
	$equipmentinfo.each(function() {
		console.log(this);
		updateValue[this.name] = $(this).val();
	    });
    }
    else {
	var updateValue = document.getElementById(id).value;
    }
    console.log("first");
    console.log(document.getElementById("gymId").value)
    console.log(id);
    console.log(updateValue);
    $.post("/api/updateinfo", {
	    "gymId": document.getElementById("gymId").value,
		"type": id,
		"text": JSON.stringify(updateValue)
		},
	"json")
    .done(function(data) {
	    console.log(data);
	})
};