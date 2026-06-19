function setCollapseExpandIcon(button) {
	// Set the collapse expand button to the correct icon
	// Strip all classes
	var outline_class = 'fa-regular';
	var solid_class = 'fa-solid';
	var minus_class = 'fa-square-minus';
	var plus_class = 'fa-square-plus';
	$(button)
		.removeClass(outline_class)
		.removeClass(solid_class)
		.removeClass(minus_class)
		.removeClass(plus_class);
	// Add the correct class based on 'collapsed'
	if ($(button).closest('.input_area').hasClass('collapsed')) {
		$(button).addClass(plus_class)
	} else {
		$(button).addClass(minus_class)
	}
	// Add the correct class based on ':hover'
	if ($(button).is(':hover')) {
		$(button).addClass(solid_class)
	} else {
		$(button).addClass(outline_class)
	}
}

// Guard if jQuery is not present
if (typeof window.jQuery !== 'undefined') {
$(document).ready(function(){
	// Collapse input_area and change icon upon click
	$('.collapse_expand_button').click(function(){
		$(this).closest('.input_area').toggleClass('collapsed')
		setCollapseExpandIcon(this)
	});
	// Highlight icon upon hover
	$('.collapse_expand_button').hover(
		handlerIn=function(){setCollapseExpandIcon(this)},
		handlerOut=function(){setCollapseExpandIcon(this)}
	)
	// Run on each
	$('.collapse_expand_button').each(function(){setCollapseExpandIcon(this)});
})
}
else {
	// eslint-disable-next-line no-console
	console.warn('input_expand_collapse: jQuery not found; collapse/expand disabled');
}


