var voteUserChange = function(gymId, userEmail, vote) {
    $.post("/api/voteuserchange", {
	    "gym_id": gymId,
	    "user_email": userEmail,
	    "vote": vote
	})
    .done(function(data) {
	    Materialize.toast(data, 4000);
	    if (data==="Thank you!") {
		console.log('thx');
		if (vote==1) {
		    document.getElementById(userEmail+"upvotes").innerHTML = parseInt(document.getElementById(userEmail+"upvotes").innerHTML)+1;
		}
		else if (vote==-1) {
		    document.getElementById(userEmail+"downvotes").innerHTML = parseInt(document.getElementById(userEmail+"downvotes").innerHTML)+1;
		}
	    }
	    else if (data==="Your vote has been changed!") {
		console.log(userEmail);
		if (vote==1) {
		    document.getElementById(userEmail+"upvotes").innerHTML = parseInt(document.getElementById(userEmail+"upvotes").innerHTML)+1;
		    document.getElementById(userEmail+"downvotes").innerHTML = parseInt(document.getElementById(userEmail+"downvotes").innerHTML)-1;
		}
		else if (vote==-1) {
		    document.getElementById(userEmail+"downvotes").innerHTML = parseInt(document.getElementById(userEmail+"downvotes").innerHTML)+1;
		    document.getElementById(userEmail+"upvotes").innerHTML = parseInt(document.getElementById(userEmail+"upvotes").innerHTML)-1;
		}
	    }
	    else {
		console.log('nahh');
	    }
	});
};