$(document).ready(function(){
    $('.toggle').click(function(){
//      SEMANTICS UI TOGGLE
        $('ul').toggleClass('pull-right');
        $('ul').toggleClass('active');
    })

    $('.ui.accordion').accordion();
    $('#founder').transition('pulse');
    $('.ui.basic.modal').modal('show');

//    EMAIL VALIDATION FOR NEWSLETTER SUBSCRIBE
    $("#submail").keyup(function(){
        var email = $("#submail").val();
        var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

         if (!filter.test(email)) {
           //alert('Please provide a valid email address');
            $("#sub_error_email").css("display", "inline-block")
            $("#sub_error_email").css("margin-bottom", "0")
            if(email == ''){
                $("#sub_error_email").text("This field cannot be blank");
           }
            else{
                $("#sub_error_email").text(email+" is not a valid email");
                email.focus;
            }
        }
        else {
            $("#sub_error_email").text("");
            $("#sub_error_email").css("display", "none")
        }
    });

//ADS CONTACT EMAIL VALIDATE
    $("#ad_email").keyup(function(){
         var email = $("#ad_email").val();
         var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

         if (!filter.test(email)) {
           //alert('Please provide a valid email address');
           $("#ad_error_email").css("display", "inline-block")
           $("#ad_error_email").css("margin-bottom", "0")
           if(email == ''){
                $("#ad_error_email").text("This field cannot be blank");
           }
           else{
               $("#ad_error_email").text(email+" is not a valid email");
               email.focus;
           }
        }
        else {
            $("#ad_error_email").text("");
            $("#ad_error_email").css("display", "none")
        }
    });

//GENERAL CONTACT EMAIL VALIDATE
    $("#c_email").keyup(function(){
         var email = $("#c_email").val();
         var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

         if (!filter.test(email)) {
           //alert('Please provide a valid email address');
           $("#error_c_email").css("display", "inline-block")
           $("#error_c_email").css("margin-bottom", "0")
           if(email == ''){
                $("#error_c_email").text("This field cannot be blank");
           }
           else{
               $("#error_c_email").text(email+" is not a valid email");
               email.focus;
           }
        }
        else {
            $("#error_c_email").text("");
            $("#error_c_email").css("display", "none")
        }
    });









/* DARK MODE */
//$(function () {
//  $(document).scroll(function () {
//    var $nav = $(".fixed-top");
//    $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
//
//    if ($nav.hasClass('scrolled')){
//        $('#brand-logo').attr("src",'/static/site_pics/site_logo_1_trans_orange_512.png');
//        $(".media").css("background-color", "blanchedalmond");
//        $("html").css("background-color", "#201f1f");
//        $("body").css("background-color", "#201f1f");
//    }
//    else{
//        $('#brand-logo').attr("src",'/static/site_pics/site_logo_1_trans.png');
//        $(".media").css("background-color", "white");
//         $("html").css("background-color", "#fffafa");
//        $("body").css("background-color", "#fffafa");
//    }
//    //document.getElementById('brand-logo').src='/static/site_pics/site_logo_1_trans_orange_512.png';
//    });
});


