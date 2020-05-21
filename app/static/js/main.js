window.onload = function () {
  /* AUTOCOMPLETE SOLUTION */
  $('#autocomplete').on('focus', function() {
    document.getElementById('searchResult').hidden=false;
    document.getElementById('close-autocomplete').hidden=false;
  });
  $('#close-autocomplete').on('click', function() {
    document.getElementById('searchResult').hidden = true;
    document.getElementById('close-autocomplete').hidden = true;
  });
  $("#autocomplete").keyup(function() {
    var search = $(this).val();

    if (search != '') {
      $.ajax({
        url: '/search-entities',
        type: 'POST',
        data: { search : search },
        dataType: 'json',
        success:function(response) {
          var len = response.length;
          $("#searchResult").empty();
          for (var i = 0; i < len; i++) {
            var id = response[i]['id'];
            var entity = response[i]['name'];
            document.getElementById('close-autocomplete').hidden=false;
            $('#searchResult').append('<li onclick="$(\'#autocomplete\').val(document.getElementById(this.id).innerText);document.getElementById(\'searchResult\').hidden=true;" id="autocomplete-option-'+id+'" value="'+id+'">'+entity+'</li>');
          }
        }
      });
    }
  });

}
