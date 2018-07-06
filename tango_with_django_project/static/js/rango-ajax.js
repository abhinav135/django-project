$(document).ready(function() {
    $('#likes').click(function() {
        var catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data){
            $('#like_count').html(data);
            $('#likes').hide();
        });
    });
    $('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });
    $('.add_page').click(function() {
        var catid = $(this).attr("data-catid");
        alert(catid);
        var title = $(this).attr("data-page_name")
        var url = $(this).attr("data-page_url")
        $.get('/rango/auto_add_page/', {category_id: catid, page_name: title , page_url: url}, function(data){
            alert();
            $('.add_page').html('Added');
        });
    });
});