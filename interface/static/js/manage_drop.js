
var show_only_progress = function(){

  $('.dz-preview').each(function(){
    var width = parseInt($(this).find('.dz-upload').css('width').split('%')[0])
    if ( width < 2 | width > 99 ) {
        $(this).hide()
    }else{ $(this).show() }
    //alert(width)
  })

}

var manage_drop = function(){

    /*
    Manage the folder dropped on the Dropzone
    */

    var list_addr = []
    var progmin = 0
    var currentpath = ""
    
    Dropzone.options.dropz = {
          paramName: "file",                                                  // The name that will be used to transfer the file
          maxFiles: 30,
          maxFilesize: 2000,                                                  // MB
          filesizeBase: 2000,
          success: function(file, response) {

             var newpath = file.fullPath

             if (list_addr.indexOf(newpath) == -1){                          // if not registered yet.
                  var find_rfp = newpath.match(/RFP/g)                         // search for RFP
                  if (!find_rfp){                                            // if there is not RFP
                    currentpath = newpath
                    $('.listfiles').append($("<li>")                         // append only BF files .. not RPF files
                                   .attr('id', newpath)
                                   .text(newpath + "....")                   // folder name
                                   .append($('<input/>')
                                      .addClass('check')
                                      .attr('id', 'box_' + newpath)
                                      .attr('type', "checkbox").css({'left':'280px', 'top':'-10px'})
                                    )  // end append
                                  ) // end append

                    list_addr.push(newpath)                 // registering the path
                   }                                        // end !find_rfp
                 }                                          // end if in registered list of paths

           },
          sending: function(file, xhr, data){

              if (typeof (file.fullPath) === "undefined") {
                        file.fullPath = file.name;
                  }
              data.append("fullPath", file.fullPath);
              $('.dz-preview').hide()                       // remove the Thumbnails
              // File upload Progress
          },
          totaluploadprogress: function(progress) {
                  show_only_progress()
                  console.log("############ progress ", progress);
                  if (progress == 100){
                      setTimeout(function(){ $('.dz-complete').find('.dz-filename').hide() }, 1000);
                  }
             }
      }; // end Dropzone.options.dropz

}
