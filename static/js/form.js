var msg = ""
var rules = {
    slug : {
        pattern: '^[a-z0-9]+$',
        required: true,
        minlength: 3,
        maxlength: 30
    },
    name : {
        required: true,
        minlength: 4,
        maxlength: 40
    }
}

var messages = {
    slug : {
        pattern: "This slug has invalid characters.\
 Slugs can only consist of letters and numbers.",
        required: "Please enter a valid slug.",
        minlength: "Slugs must be 3 or more characters.",
        maxlength: "Slugs must be 30 characters or less.\
 Keep in mind that this will become part of the planet's URL;\
 shorter slugs help keep the URL short as well."
    },
    name : "Please enter a valid planet name.\
 Names can have 4-40 characters."
}

$(document).ready(function(){

    // validate form fields
    $('#new-planet').validate({
        rules: rules,
        messages: messages,
        submitHandler : save

    });
}); // end ready function

// additional validator method for slug regex pattern
$.validator.addMethod("pattern", function(value, element, param) {
    if (this.optional(element)) {
        console.log("this.optional")
        return true;
    }
    if (typeof param === "string") {
        param = new RegExp(param);
        console.log("RegExp test")
    }
    return param.test(value);
});

function set_message(txt){
    $("#status-message").text(txt);
    $("#status-message").show();
}

function clear_message(){
    $("#status-message").text("");
    $("#status-message").hide();
}

function save(){
    console.log('Saving new planet');

    planet_name = $("#name").val();
    console.log('Planet name: ' + planet_name)

    slug = $("#slug").val();
    console.log('Planet slug: ' + slug)

    $.ajax({
        url: "/ws/planet/new",
        type: "POST",
        data : {
            slug : slug,
            planet_name : planet_name
        },
        success: function(json)
        {
            // add "success" message to tell user save was successful.
            var success_msg = 'New planet saved. Now redirecting you to the Admin page to add feeds.'
            console.log(success_msg);

            // load planet admin page so they can add more detail.
            window.location.assign("/planet/" + encodeURIComponent(slug) + "/admin");
        },
        error: function(xmlhttp, txtStatus, error)
        {
            if (xmlhttp.status == 403) {
                var fail_msg ="Sorry, there is already a planet with the slug '" + slug + "', please use another slug. ";
            } else if (xmlhttp.statusText == "BadRequest") {
                var fail_msg ="Sorry, the planet data does not meet database constraints. ";
            } else {
                var fail_msg ="Uhm. Something unique and interesting is happening. Something not so good. ";
            }
            fail_msg += xmlhttp.status + " " + error;
            console.log(fail_msg);
            set_message(fail_msg);
            console.log("error: " + error);
        }
  });
}
