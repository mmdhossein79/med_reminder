/* Template Name: Doctris - Doctor Appointment Booking System
   Author: Shreethemes
   Website:  /
   Mail: support@shreethemes.in
   File Description: Main JS file of the template
*/

! function($) {
    "use strict"; 
    // Loader 
    $(window).on('load', function() {
        $('#status').fadeOut();
        $('#preloader').delay(350).fadeOut('slow');
        $('body').delay(350).css({
            'overflow': 'visible'
        });
    });
    
    // Menu
    $('.navbar-toggle').on('click', function (event) {
        $(this).toggleClass('open');
        $('#navigation').slideToggle(400);
    });

$('.navigation-menu a').on('click', function(event) {
    var $anchor = $(this);
    var href = $anchor.attr('href');

    // چک کردن اینکه href معتبر است
    if (href && href !== 'javascript:void(0)' && href.startsWith('#')) {
        var target = $(href); // دریافت عنصر هدف

        // بررسی اینکه عنصر هدف وجود دارد
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top // اسکرول به عنصر هدف
            }, 2000, 'easeInOutExpo');
        } else {
            console.warn('Target element not found for href:', href);
        }

        event.preventDefault(); // جلوگیری از رفتار پیش‌فرض لینک
    }
});

$(document).ready(function() {
    $('.parent-menu-item > a').on('click', function(e) {
        var $submenu = $(this).next('.submenu');

        // بستن زیرمنوهای دیگر در صورت نیاز
        $('.submenu').not($submenu).slideUp();

        // باز و بسته کردن زیرمنو کلیک شده
        $submenu.slideToggle();

        e.preventDefault();  // جلوگیری از رفتن به لینک
    });
});

    
    //Tooltip
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
    
    //Scrollspy
    $("#navigation").scrollspy({
        offset: 50
    });

    //Sticky
    $(window).scroll(function() {
        var scroll = $(window).scrollTop();

        if (scroll >= 50) {
            $(".sticky").addClass("nav-sticky");
        } else {
            $(".sticky").removeClass("nav-sticky");
        }
    });
    
    $('.mouse-down').on('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top - 72
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });

    // BACK TO TOP
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn();
        } else {
            $('.back-to-top').fadeOut();
        }
    });
    //Feather icon
    feather.replace()

    //Twenty twenty slider
    $( window ).on( "load", function() {
        $(".twentytwenty-container[data-orientation!='vertical']").twentytwenty({default_offset_pct: 0.5});
        $(".twentytwenty-container[data-orientation='vertical']").twentytwenty({default_offset_pct: 0.5, orientation: 'vertical'});
    });
}(jQuery)