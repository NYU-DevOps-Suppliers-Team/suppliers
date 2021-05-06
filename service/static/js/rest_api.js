$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#supplier_id").val(res.id);
        $("#supplier_name").val(res.name);
        $("#supplier_email").val(res.email);
        $("#supplier_address").val(res.address);
        $("#supplier_phone_number").val(res.phone_number);
        res.available ? $("#supplier_available").prop("checked", true): $("#supplier_unavailable").prop("checked", true);  
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#supplier_name").val("");
        $("#supplier_email").val("");
        $("#supplier_address").val("");
        $("#supplier_phone_number").val("");
        $("#supplier_available").prop("checked", true);
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Supplier
    // ****************************************

    
    $("#create-btn").click(function () {
        var name = $("#supplier_name").val();
        var email = $("#supplier_email").val();
        var address = $("#supplier_address").val();
        var phone_number = $("#supplier_phone_number").val() || null;
        var available = $('input[name="supplier_available"]:checked').val() == "true";

        var data = {
            "name": name,
            "email": email,
            "address": address,
            "phone_number": phone_number,
            "available": available,
            "products" : []
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/suppliers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
            retrieveOrderedList()
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Supplier
    // ****************************************

    $("#update-btn").click(function () {

        var supplier_id = $("#supplier_id").val();
        var name = $("#supplier_name").val();
        var email = $("#supplier_email").val();
        var address = $("#supplier_address").val();
        var phone_number = $("#supplier_phone_number").val();
        var available = $('input[name="supplier_available"]:checked').val() == "true";

        var data = {
            "name": name,
            "email": email,
            "address": address,
            "phone_number": phone_number,
            "available": available,
            "products" : []
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/suppliers/" + supplier_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
            retrieveOrderedList()
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a SUPPLIER
    // ****************************************

    $("#retrieve-btn").click(function () {

        var supplier_id = $("#supplier_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Supplier
    // ****************************************

    $("#delete-btn").click(function () {

        var supplier_id = $("#supplier_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Supplier has been Deleted!")
            retrieveOrderedList()
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#supplier_id").val("");
        clear_form_data()
        retrieveOrderedList()
    });

    // ****************************************
    // Search for a Supplier
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#supplier_name").val();
        var email = $("#supplier_email").val();
        var address = $("#supplier_address").val();
        var phone_number = $("#supplier_phone_number").val();
        var available = $('input[name="supplier_available"]:checked').val() == "true";

        var queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (email) {
            queryString += 'email=' + email
        }
        if (address) {
            queryString += 'address=' + address
        }
        if (phone_number) {
            queryString += 'phone_number=' + phone_number
        }
        if (queryString.length > 0) {
            queryString += '&available=' + available
        } else {
            queryString += 'available=' + available
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            var firstSupplier = "";
            $("#table-content").empty();
            for(var i = 0; i < res.length; i++) {
                var supplier = res[i];
                var tr = '<tr>' ; 
               // create a new Label Text
                   tr += '<td>' + supplier.id  + '</td>';
                   tr += '<td>' + supplier.name + '</td>';
                   tr += '<td>' + supplier.email + '</td>';  
                   tr += '<td>' + supplier.address + '</td>';  
                   tr += '<td>' + supplier.phone_number + '</td>';
                   tr += supplier.available ? '<td>' + supplier.available + '</td>': '<td class="unavailable">' + supplier.available + '</td>';  
                   tr +='</tr>';
                
                $("#table-content").append(tr);
                if (i == 0) {
                    firstSupplier = supplier;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstSupplier != "") {
                update_form_data(firstSupplier)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // List for a Supplier
    // ****************************************

    function retrieveOrderedList(e) {

        var sort_by = e ? $(e.target).attr('sort') : 'id';

        var queryString = 'sort_by=' + sort_by;

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers?" + queryString,
            contentType: "application/json",
            data: ''
        })
        
        ajax.done(function(res){

            var firstSupplier = "";
            $("#table-content").empty();
            for(var i = 0; i < res.length; i++) {
                var supplier = res[i];
                var tr = '<tr>' ; 
               // create a new Label Text
                   tr += '<td>' + supplier.id  + '</td>';
                   tr += '<td>' + supplier.name + '</td>';
                   tr += '<td>' + supplier.email + '</td>';  
                   tr += '<td>' + supplier.address + '</td>';  
                   tr += '<td>' + supplier.phone_number + '</td>';
                   tr += supplier.available ? '<td>' + supplier.available + '</td>': '<td class="unavailable">' + supplier.available + '</td>';  
                   tr +='</tr>';
                
                $("#table-content").append(tr);
                if (i == 0) {
                    firstSupplier = supplier;
                }
            }

            $("#search_results").append('</table>');
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    }

    $("#list-btn").click(retrieveOrderedList);
    $("#list-by-name-btn").click(retrieveOrderedList);
    $("#list-by-email-btn").click(retrieveOrderedList);
    $("#list-by-address-btn").click(retrieveOrderedList);
    $("#list-by-id-btn").click(retrieveOrderedList);

    retrieveOrderedList()

})
