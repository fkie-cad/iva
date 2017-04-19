/**
 * Created by LABS on 12.08.2016.
 */

$('document').ready(function(){

    $('#cve_matches').jplist({
	    itemsBox: '.list'
        ,itemPath: '.list-item'
		,panelPath: '.jplist-panel'
	});

	$('#confirmed_cve_matches').jplist({
	    itemsBox: '.list'
        ,itemPath: '.list-item'
		,panelPath: '.jplist-panel'
	});

	$('#removed_cve_matches').jplist({
	    itemsBox: '.list'
        ,itemPath: '.list-item'
		,panelPath: '.jplist-panel'
	});

	$("body").on('click', '.show_cpes', function () {
    	var cve_id = $(this).attr('value');
    	var cpes = $('#'+cve_id);
		var img_show = $('#show_'+cve_id);
		var img_hide = $('#hide_'+cve_id);
		cpes.css('visibility', 'visible');
		cpes.css('width', '100%');
		cpes.css('height', '100%');
		img_hide.css('visibility', 'visible');
		img_hide.css('width', '100%');
		img_hide.css('height', '100%');
		img_show.css('visibility', 'hidden');
		img_show.css('width', '0px');
		img_show.css('height', '0px');

    });

	$("body").on('click', '.hide_cpes', function () {
    	var cve_id = $(this).attr('value');
    	var cpes = $('#'+cve_id);
		var img_show = $('#show_'+cve_id);
		var img_hide = $('#hide_'+cve_id);
		cpes.css('visibility', 'hidden');
		cpes.css('width', '0px');
		cpes.css('height', '0px');
		img_show.css('visibility', 'visible');
		img_show.css('width', '100%');
		img_show.css('height', '100%');
		img_hide.css('visibility', 'hidden');
		img_hide.css('width', '0px');
		img_hide.css('height', '0px');
    });

	var select_element = document.getElementById('show_removed');
	if (location.href.indexOf('?option=show_removed') != -1 ||
			location.href.indexOf('?option=ordered_by_year_desc_show_removed') != -1 ||
			location.href.indexOf('?option=ordered_by_year_asc_show_removed') != -1) {
		select_element.checked = true
	} else if (location.href.indexOf('?option=hide_removed') != -1 ||
			location.href.indexOf('?option=ordered_by_year_desc_hide_removed') != -1 ||
			location.href.indexOf('?option=ordered_by_year_asc_hide_removed') != -1) {
		select_element.checked = false
	}

});


function show_vendor_cves() {
	var vendor = document.getElementById('vendor').value;
	document.location.href = '?option=show_vendor_cves&vendor='+vendor+'&product=all'
}


function show_vendor_product_cves() {
	var vendor = document.getElementById('vendor').value;
	var product = encodeURIComponent(document.getElementById('product').value);
	document.location.href = '?option=show_vendor_cves&vendor='+vendor+'&product='+product;
}

function show_removed() {
	var select_element = document.getElementById('show_removed');
    var vendor = document.getElementById('vendor').value;
	var product = encodeURIComponent(document.getElementById('product').value);
	if (select_element.checked) {
		if (location.href.indexOf('ordered_by_year_desc') != -1) {
			document.location.href = '?option=ordered_by_year_desc_show_removed&vendor='+vendor+'&product='+product;
		} else if (location.href.indexOf('ordered_by_year_asc') != -1) {
            document.location.href = '?option=ordered_by_year_asc_show_removed&vendor='+vendor+'&product='+product;
        } else {
			document.location.href = '?option=show_removed&vendor='+vendor+'&product='+product;
		}
	} else {
		if (location.href.indexOf('ordered_by_year_desc') != -1) {
			document.location.href = '?option=ordered_by_year_desc_hide_removed&vendor='+vendor+'&product='+product;
		} else if (location.href.indexOf('ordered_by_year_asc') != -1) {
            document.location.href = '?option=ordered_by_year_asc_hide_removed&vendor='+vendor+'&product='+product;
        } else {
			document.location.href = '?option=hide_removed&vendor='+vendor+'&product='+product;
		}
	}
}

function oder_by_year_desc() {
	var select_element = document.getElementById('show_removed');
    var vendor = document.getElementById('vendor').value;
	var product = encodeURIComponent(document.getElementById('product').value);
    if (select_element.checked) {
		document.location.href = '?option=ordered_by_year_desc_show_removed&vendor='+vendor+'&product='+product;
	} else {
		document.location.href = '?option=ordered_by_year_desc_hide_removed&vendor='+vendor+'&product='+product;
	}
}


function oder_by_year_asc() {
	var select_element = document.getElementById('show_removed');
    var vendor = document.getElementById('vendor').value;
	var product = encodeURIComponent(document.getElementById('product').value);
    if (select_element.checked) {
		document.location.href = '?option=ordered_by_year_asc_show_removed&vendor='+vendor+'&product='+product;
	} else {
		document.location.href = '?option=ordered_by_year_asc_hide_removed&vendor='+vendor+'&product='+product;
	}
}

function modify_cve_match(cve_id, software_id, option) {
    $.ajax({
        type: "POST",
        url: "cve_matches.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            cve_id: cve_id,
            software_id: software_id,
            option: option
        },
        success: function(result) {
            location.reload();
        }
    });
}

function modify_cve_matches_group(cve_id_master, software_id, option) {
    $.ajax({
        type: "POST",
        url: "grouped_cve_matches.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            cve_id_master: cve_id_master,
            software_id: software_id,
            option: option
        },
		beforeSend: function() {
			$("#matches_container").hide();
			$("#matches_container_title").hide();
        	$("#loading").html('<div class="info-msg">request is being processed, please wait</div>');
    	},
		success: function(result) { location.reload(); }
    });
}






