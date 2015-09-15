var matchFields = function(field, specific) {
    field1 = document.getElementById(field+specific+"1").value;
    field2 = document.getElementById(field+specific+"2").value;
    if (field1 != field2) {
	Materialize.toast("Please enter matching " + field + "s", 4000);
        return false;
    }
    return true;
};
var validate = function(form, user) {
    if (form==="login") {
	var email = document.getElementById("email" + user).value;
	var password = document.getElementById("password" + user).value;
    }
    else if (form==="signup") {
	var email = document.getElementById("email" + user + "1").value;
	var password = document.getElementById("password" + user + "1").value;
    }
    else {
	Materialize.toast("Something went wrong", 4000);
	return false;
    }
    if (email.indexOf("@")==-1 || email.indexOf(".")==-1 || email.length<7) {
	Materialize.toast("Please enter a valid email", 4000);
	return false;
    }
    if (password.length<5) {
	Materialize.toast("Please enter a password of at least length 5", 4000);
	return false;
    }
    return true;
};