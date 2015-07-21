var matchFields = function(field) {
    field1 = document.getElementById(field+"1").value;
    field2 = document.getElementById(field+"2").value;
    if (field1 != field2) {
	alert("Please enter matching " + field + "s");
        return false;
    }
    return true;
};
var validate = function(form) {
    if (form==="login") {
	var email = document.getElementById("email").value;
	var password = document.getElementById("password").value;
    }
    else if (form==="signup") {
	var email = document.getElementById("email1").value;
	var password = document.getElementById("password1").value;
    }
    else {
	alert("Something went wrong");
	return false;
    }
    if (email.indexOf("@")==-1 || email.indexOf(".")==-1 || email.length<7) {
	alert("Please enter a valid email");
	return false;
    }
    if (password.length<5) {
	alert("Please enter a password of at least length 5");
	return false;
    }
    return true;
};