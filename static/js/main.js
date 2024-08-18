$(document).ready(function() {
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })

    // Handle chore checkbox changes
    $('.chore-checkbox').on('change', function() {
        var horseId = $(this).data('horse-id');
        var choreId = $(this).data('chore-id');
        var completed = $(this).is(':checked');

        $.ajax({
            url: '/update_chore',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                horse_id: horseId,
                chore_id: choreId,
                completed: completed
            }),
            success: function(response) {
                if (response.success) {
                    console.log('Chore updated successfully');
                }
            }
        });
    });

    // Handle add horse form submission
    $('#add-horse-form').on('submit', function(e) {
        e.preventDefault();
        var horseData = {
            name: $('#horse-name').val(),
            image: $('#horse-image').val(),
            info: $('#horse-info').val()
        };

        $.ajax({
            url: '/add_horse',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(horseData),
            success: function(response) {
                if (response.success) {
                    location.reload();
                }
            }
        });
    });

    // Handle add chore form submission
    $('#add-chore-form').on('submit', function(e) {
        e.preventDefault();
        var choreData = {
            name: $('#chore-name').val(),
            category: $('#chore-category').val()
        };

        $.ajax({
            url: '/add_chore',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(choreData),
            success: function(response) {
                if (response.success) {
                    location.reload();
                }
            }
        });
    });

    // Handle remove horse
    $('.remove-horse').on('click', function() {
        var horseId = $(this).data('horse-id');
        if (confirm('Are you sure you want to remove this horse?')) {
            $.ajax({
                url: '/remove_horse',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ horse_id: horseId }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    }
                }
            });
        }
    });

    // Handle remove chore
    $('.remove-chore').on('click', function() {
        var choreId = $(this).data('chore-id');
        if (confirm('Are you sure you want to remove this chore?')) {
            $.ajax({
                url: '/remove_chore',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ chore_id: choreId }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    }
                }
            });
        }
    });

    $('.edit-chore').click(function() {
        const choreId = $(this).data('chore-id');
        const newName = prompt('Enter new chore name:');
        if (newName) {
            $.ajax({
                url: '/edit_chore',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ chore_id: choreId, updated_data: { name: newName } }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    }
                }
            });
        }
    });
    
    // Delete chore
    $('.delete-chore').click(function() {
        const choreId = $(this).data('chore-id');
        if (confirm('Are you sure you want to delete this chore?')) {
            $.ajax({
                url: '/delete_chore',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ chore_id: choreId }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    }
                }
            });
        }
    });
    
    
    
    // Handle change password form submission
    $('#change-password-form').on('submit', function(e) {
        e.preventDefault();
        var newPassword = $('#new-password').val();

        $.ajax({
            url: '/change_password',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ new_password: newPassword }),
            success: function(response) {
                if (response.success) {
                    alert('Password changed successfully');
                    $('#new-password').val('');
                }
            }
        });
    });
});