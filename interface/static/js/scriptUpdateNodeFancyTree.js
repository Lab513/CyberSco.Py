function updateNodePosition(my_id, my_key) {
    var node = $("#tree").fancytree("getTree").getNodeByKey(my_key);

    if (!node) {
        console.log("Error: No node found!");
        return ;
    }
    //maybe make a req to node to get positions instead of just take it form the DOM
    var newPosX = $("#position-x").text();
    var newPosY = $("#position-y").text();
    var newPosZ = $("#position-z").text();
    newgate = "none";
    if (!parseFloat(newPosX) || !parseFloat(newPosY) || !parseFloat(newPosZ)) {
        console.log("Bad Position, setting X, Y, Z to 0");
        newPosX = "0";
        newPosY = "0";
        newPosZ = "0";
    }
    node.data.xPosition = parseFloat(newPosX);
    node.data.yPosition = parseFloat(newPosY);
    node.data.zPosition = parseFloat(newPosZ);
    node.data.gate = 'none';
    $("#" + my_id).text("X:Y:Z:Gate => " +
              newPosX + ":" + newPosY + ":" +
              newPosZ + ":" + newgate);

}

function goToNodePosition(data_id_position_to_go) {
    var position = $("#" + data_id_position_to_go).text();
    console.log("GOING TO " + position);
}

function updateAutoFocus(my_id, my_key) {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateAutoFocus()!");
        return ;
    }
    if ($("#select-af-objectif :selected").text() != "Select your objective...") {
        node.data.objectif = $("#select-af-objectif :selected").text();
    }
    if ($('#z-offset-value').text() != "undefined") {
        node.data.zoffset = parseInt($('#z-offset-value').text());
    }
    $("#" + my_id).text("Objectif: " + node.data.objectif + " Z-Offset: " + node.data.zoffset);
}

function updateZSPSC() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateZSPSC()!");
        return ;
    }
    if ($("#setting-channel-zs-sc-modal :selected").text() != "Select a setting channel...") {
        node.data.setting_channel_name = $("#setting-channel-zs-sc-modal :selected").text();
    }
    node.data.far_limit = parseInt($("#far-limit-zs-sc-modal").val());
    node.data.near_limit = parseInt($("#near-limit-zs-sc-modal").val());
    node.data.step = parseInt($("#step-zs-sc-modal").val());
    node.data.exposure_time = parseInt($("#exposure-time-zs-sc-modal").val());
    node.data.keep_shutter_on_wzs = $('#keep-shutter-on-zs-sc-modal').is(':checked');
    document.getElementById(node.key + "-info").innerHTML = 'far/near limit: ' +node.data.far_limit+'um/'+node.data.near_limit+'um Step: '+node.data.step+'um SC: '+node.data.setting_channel_name+' ET: '+node.data.exposure_time+'ms';
    console.log("OK");
}

function updateZSPSCPMM() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateZSPSCMM()!");
        return ;
    }
    if ($("#setting-channel-zs-sc-mm-modal :selected").text() != "Select a setting channel...") {
        node.data.setting_channel_name = $("#setting-channel-zs-sc-mm-modal :selected").text();
    }
    if ($("#mosaic-mask-zs-sc-mm-modal :selected").text() != "Select a mosaic mask...") {
        node.data.mosaic_mask_name = $("#mosaic-mask-zs-sc-mm-modal :selected").text();
    }
    node.data.far_limit = parseInt($("#far-limit-zs-sc-mm-modal").val());
    node.data.near_limit = parseInt($("#near-limit-zs-sc-mm-modal").val());
    node.data.step = parseInt($("#step-zs-sc-mm-modal").val());
    node.data.exposure_time = parseInt($("#exposure-time-zs-sc-mm-modal").val());
    node.data.keep_shutter_on_wzs = $('#keep-shutter-on-zs-sc-mm-modal').is(':checked');
    document.getElementById(node.key + "-info").innerHTML = 'far/near limit: ' +node.data.far_limit+'um/'+node.data.near_limit+'um Step: '+node.data.step+'um SC: '+node.data.setting_channel_name+' MM: '+node.data.mosaic_mask_name+' ET: '+node.data.exposure_time+'ms';
    console.log("OK");
}

function updateSPPSC() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateSPPSC()!");
        return ;
    }

    if ($("#setting-channel-sp-sc-modal :selected").text() != "Select a setting channel...") {
        node.data.setting_channel_name = $("#setting-channel-sp-sc-modal :selected").text();
    }
    node.data.exposure_time = parseInt($("#exposure-time-sp-sc-modal").val());
    document.getElementById(node.key + "-info").innerHTML = 'SC: ' + node.data.setting_channel_name + ' ET: ' + node.data.exposure_time + 'ms';
}

function updateSPPSCPMM() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateSPPSCPMM()!");
        return ;
    }

    if ($("#setting-channel-sp-sc-mm-modal :selected").text() != "Select a setting channel...") {
        node.data.setting_channel_name = $("#setting-channel-sp-sc-mm-modal :selected").text();
    }
    if ($("#mosaic-mask-sp-sc-mm-modal :selected").text() != "Select a mosaic mask...") {
        node.data.mosaic_mask_name = $("#mosaic-mask-sp-sc-mm-modal :selected").text();
    }
    node.data.exposure_time = parseInt($("#exposure-time-sp-sc-mm-modal").val());
    document.getElementById(node.key + "-info").innerHTML = 'SC: ' + node.data.setting_channel_name + ' MM: ' + node.data.mosaic_mask_name + ' ET: ' + node.data.exposure_time + 'ms';
}

function updateDelay() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateDelay()!");
        return ;
    }

    node.data.time = parseInt($("#delay-modal").val());
    document.getElementById(node.key + "-info").innerHTML = 'Delay (ms): ' + node.data.time;
}

function updateSequence() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateDelay()!");
        return ;
    }

    node.data.time_per_repetition = parseInt($("#time-per-repetition-modal").val());
    node.data.nb_repetition = parseInt($("#nb-repetition-modal").val());
    document.getElementById(node.key + "-info").innerHTML = 'Nb rep: ' + node.data.nb_repetition + ' Time per rep: ' + node.data.time_per_repetition + 'min';
}

function updateMicroFluidicsM() {
    var node = $("#tree").fancytree("getActiveNode");

    if (!node) {
        console.log("Error: No node found in updateDelay()!");
        return ;
    }
    node.data.valve_1 = $('#valve-1-modal :selected').text();
    node.data.valve_2 = $('#valve-2-modal :selected').text();
    node.data.valve_3 = $('#valve-3-modal :selected').text();
    node.data.valve_4 = $('#valve-4-modal :selected').text();
    node.data.valve_5 = $('#valve-5-modal :selected').text();
    document.getElementById(node.key + "-info").innerHTML = 'V1: ' + node.data.valve_1 + ' V2: ' + node.data.valve_2 + ' V3: ' + node.data.valve_3 + ' V4: ' + node.data.valve_4 + ' V5: ' + node.data.valve_5;
}
