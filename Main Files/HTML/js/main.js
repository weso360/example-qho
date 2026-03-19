(function ($) {
 "use strict";

/*----------------------------
1. Full page Preloader
-----------------------------*/
    jQuery(window).on('load', function() {
      jQuery("#loader").fadeOut();
      jQuery("#loader_wrapper").delay(350).fadeOut("slow");
    });


/*----------------------------
2. jQuery MeanMenu
------------------------------ */
	jQuery('nav#dropdown').meanmenu();	

/*--------------------------
 3. Sticky Menu 
---------------------------- */
	$(window).on('scroll', function(){
		if( $(window).scrollTop()>900 ){
			$('#sticky').addClass('sticky');
			} else {
			$('#sticky').removeClass('sticky');
		}
	});	

/*----------------------------
4. wow js active
------------------------------ */
	new WOW().init();
/*----------------------------
5. Toggle Search box
------------------------------ */
	//Header search box
	$( ".search-ico" ).on("click",function() {
	  $( ".search-box" ).slideToggle("slow");
	});
	$( ".close-search" ).on("click",function() {
	  $( ".search-box" ).slideToggle("slow");
	});
/*----------------------------
6. owl active
------------------------------ */  
	//Services owl slider
	$(".services-slider").owlCarousel({
		autoPlay: false, 
		slideSpeed:2000,
		pagination:true,
		navigation:false,	  
		items : 4,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,4],
		itemsDesktopSmall : [992,3],
		itemsTablet: [768,2],
		itemsMobile : [479,1],
	});

	//Shop owl slider
	$(".shop-slider").owlCarousel({
		autoPlay: false, 
		slideSpeed:2000,
		pagination:true,
		navigation:false,	  
		items : 4,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,4],
		itemsDesktopSmall : [992,3],
		itemsTablet: [768,2],
		itemsMobile : [479,1],
	});

	//Testimonial owl  slider
	$(".testimonial-slider").owlCarousel({
		autoPlay: true, 
		slideSpeed:2000,
		pagination:false,
		navigation:true,	  
		items : 1,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,1],
		itemsDesktopSmall : [992,1],
		itemsTablet: [768,1],
		itemsMobile : [479,1],
	});


	//Gallery owl slider
	$(".gallery-slider").owlCarousel({
		autoPlay: true, 
		slideSpeed:2000,
		pagination:false,
		navigation:false,	  
		items : 5,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,4],
		itemsDesktopSmall : [992,3],
		itemsTablet: [768,2],
		itemsMobile : [479,1],
	});

	//Brand owl slider
	$(".brand-slider").owlCarousel({
		autoPlay: true, 
		slideSpeed:2000,
		pagination:true,
		navigation:false,	  
		items : 6,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,5],
		itemsDesktopSmall : [992,4],
		itemsTablet: [768,3],
		itemsMobile : [479,2],
	});

	//About owl slider
	$(".about-img-slider").owlCarousel({
		autoPlay: true, 
		slideSpeed:2000,
		pagination:false,
		navigation:true,	  
		items : 1,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,1],
		itemsDesktopSmall : [992,1],
		itemsTablet: [768,1],
		itemsMobile : [479,1],
	});

	//Product owl slider
	$(".prod-slider").owlCarousel({
		autoPlay: true, 
		slideSpeed:2000,
		pagination:false,
		navigation:false,	  
		items : 4,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,4],
		itemsDesktopSmall : [992,3],
		itemsTablet: [768,2],
		itemsMobile : [479,1],
	});

	//testimonial owl slider
	$(".testi-slider").owlCarousel({
		autoPlay: true, 
		slideSpeed:2000,
		pagination:false,
		navigation:false,	  
		items : 1,
		/* transitionStyle : "fade", */    /* [This code for animation ] */
		navigationText:["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
		itemsDesktop : [1199,1],
		itemsDesktopSmall : [992,1],
		itemsTablet: [768,1],
		itemsMobile : [479,1],
	});
/*--------------------------
7. bxslider active
---------------------------- */ 
	//Team on click slider
	$('.team-con').bxSlider({
		pagerCustom: '.thumb-list',
		mode: 'fade',
	});
	
	//Single product on click slider
	$('.productmain').bxSlider({
		pagerCustom: '.thumbnails',
		mode: 'fade',
	});
/*----------------------------
8. isotope active
------------------------------ */     
	var $grid = $('.grid').isotope({
	    itemSelector: '.grid-item',
	    stagger: 30
	  });

	  $('.filter-demo').on( 'click', '.button', function() {
	    var filterValue = $(this).attr('data-filter');
	    $grid.isotope({ filter: filterValue });
	  });

	  // change is-checked class on buttons
	  $('.filter').each( function( i, buttonGroup ) {
	    var $buttonGroup = $( buttonGroup );
	    $buttonGroup.on( 'click', '.button', function() {
	      $buttonGroup.find('.is-checked').removeClass('is-checked');
	      $( this ).addClass('is-checked');
	    });
	  });

/*----------------------------
9. magnific Popup active
------------------------------ */
	$('#gallery').magnificPopup({
		delegate: 'a',
		type: 'image',
		closeOnContentClick: false,
		closeBtnInside: false,
		mainClass: 'mfp-with-zoom mfp-img-mobile',
		image: {
			verticalFit: true,
			titleSrc: function(item) {
				return item.el.attr('title') + ' &middot; <a class="image-source-link" href="'+item.el.attr('data-source')+'" target="_blank">image source</a>';
			}
		},
		gallery: {
			enabled: true
		},
		zoom: {
			enabled: true,
			duration: 300, // don't foget to change the duration also in CSS
			opener: function(element) {
				return element.find('img');
			}
		}
		
	});
/*--------------------------
10. jarallax active
---------------------------- */
	//Backgroud image parallax
	$('.jarallax').jarallax({
		speed: 0.5
	});

   
/*----------------------------
11. range-slider active
------------------------------ */  
	$( "#range-price" ).slider({
		range: true,
		min: 0,
		max: 1200,
		values: [ 0, 875 ],
		slide: function( event, ui ) {
	$( "#price" ).val("$" + ui.values[ 0 ] + " - " +  " $" + ui.values[ 1 ]  );
	}
	});
	//Range values
	$( "#price" ).val( "$" + $( "#range-price" ).slider( "values", 0 ) +
	" - " + " $" + $( "#range-price" ).slider( "values", 1 )); 

/*----------------------------
12. list grid view active
------------------------------ */
	//List Product
	$('#listview').on('click',function(event){
		event.preventDefault();
		$('#products .item').addClass('list-item');
	});

	//Grid Product
    $('#gridview').on('click',function(event){
    	event.preventDefault();
    	$('#products .item').removeClass('list-item');
    	$('#products .item').addClass('grid-item'); 
    });


/*--------------------------
13. Product cart added value
---------------------------- */	
	$(".vertical-spin").TouchSpin({
		verticalbuttons: true,
		verticalupclass: 'fa fa-plus',
		verticaldownclass: 'fa fa-minus'
	});

/*--------------------------
14. Counter Animation
---------------------------- */
	var counterAnim = $('.count');
	if( counterAnim.length > 0 ){
		counterAnim.counterUp({ delay: 10,
        time: 1000});
	}

/*--------------------------
15. scrollUp
---------------------------- */	
	$("#totop").hide();
	$(function toTop() {
		$(window).scroll(function () {
			if ($(this).scrollTop() > 100) {
				$('#totop').fadeIn();
			} else {
				$('#totop').fadeOut();
			}
		});

		$('#totop').on('click',function () {
			$('body,html').animate({
				scrollTop: 0
			}, 800);
			return false;
		});
	});		   
 
 
})(jQuery); 