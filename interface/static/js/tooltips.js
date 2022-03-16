
var make_ttip = function(){
 
            $('.ttip').hover(function(){
            var elemname = $(this).children().attr('ttname')   // children()
            var ttext = '#' + 'tt_' + $(this).children().attr('name')  // children()
            // ttext.hide()
            var txt = $(ttext).html()
            // alert(txt)
            var pos = $(this).offset()                       //  Taking the position of the object
            var t_title = $('<p/>').text(elemname).css({'font-weight': 'bold', 'text-align':'center'})
            var t_body = $('<p/>').text(txt)
            // alert(t.text())
            $('#ttip').empty()
                    .append(t_title)
                    .append(t_body)
                    .css('left', parseInt(pos.left-170))       // tooltip position in x
                    .css('top', pos.top+70)                    // tooltip position in y
                    $('#ttip').hide();
           },
               function(){
                     $('#ttip').hide()          // Hiding the tooltip when going out of the object.
         }) // end hover
 

}