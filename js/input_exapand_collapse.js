function setCollapseExpandIcon(button) {
	// Set the collapse expand button to the correct icon
	// Strip all classes
	var outline_class = 'far';
	var solid_class = 'fas';
	var minus_class = 'fa-minus-square';
	var plus_class = 'fa-plus-square';
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
