$(document).ready(function () {
  // Initialize popovers
  var popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]'),
  );
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Handle chore checkbox changes
  $(".chore-checkbox").on("change", function () {
    var horseId = $(this).data("horse-id");
    var choreId = $(this).data("chore-id");
    var completed = $(this).is(":checked");

    $.ajax({
      url: "/update_chore",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        horse_id: horseId,
        chore_id: choreId,
        completed: completed,
      }),
      success: function (response) {
        if (response.success) {
          console.log("Chore updated successfully");
        }
      },
    });
  });

  // Handle add horse form submission
  $("#add-horse-form").on("submit", function (e) {
    console.log("I am Creating a Horse");
    e.preventDefault();
    var horseData = {
      name: $("#horse-name").val(),
      image: $("#horse-image").val(),
      info: $("#horse-info").val(),
    };

    console.log({ horseData });

    $.ajax({
      url: "/add_horse",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(horseData),
      success: function (response) {
        if (response.success) {
          location.reload();
        }
      },
    });
  });

  // Handle add chore form submission
  $("#add-chore-form").on("submit", function (e) {
    e.preventDefault();
    var choreData = {
      name: $("#chore-name").val(),
      category: $("#chore-category").val(),
    };

    $.ajax({
      url: "/add_chore",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(choreData),
      success: function (response) {
        if (response.success) {
          location.reload();
        }
      },
    });
  });

  $('.edit-horse').click(function() {
    const horseId = $(this).data('horse-id');
    // Fetch horse data and populate the form
    $.get(`/get_horse/${horseId}`, function(data) {
        $('#edit-horse-id').val(data._id);
        $('#edit-horse-name').val(data.name);
        $('#edit-horse-image').val(data.image);
        $('#edit-horse-info').val(data.info);
        $('#edit-horse-modal').modal('show');
    });
});

// Handle edit horse
$('#edit-horse-form').submit(function(e) {
    e.preventDefault();
    const horseId = $('#edit-horse-id').val();
    const horseData = {
        name: $('#edit-horse-name').val(),
        image: $('#edit-horse-image').val(),
        info: $('#edit-horse-info').val()
    };
    $.ajax({
        url: `/edit_horse/${horseId}`,
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

  // Handle remove horse
  $(".remove-horse").on("click", function () {
    var horseId = $(this).data("horse-id");
    if (confirm("Are you sure you want to remove this horse?")) {
      $.ajax({
        url: "/remove_horse",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ horse_id: horseId }),
        success: function (response) {
          if (response.success) {
            location.reload();
          }
        },
      });
    }
  });

  // Handle remove chore
  $(".remove-chore").on("click", function () {
    var choreId = $(this).data("chore-id");
    if (confirm("Are you sure you want to remove this chore?")) {
      $.ajax({
        url: "/remove_chore",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ chore_id: choreId }),
        success: function (response) {
          if (response.success) {
            location.reload();
          }
        },
      });
    }
  });

  $(".edit-chore").click(function () {
    const choreId = $(this).data("chore-id");
    const newName = prompt("Enter new chore name:");
    if (newName) {
      $.ajax({
        url: "/edit_chore",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
          chore_id: choreId,
          updated_data: { name: newName },
        }),
        success: function (response) {
          if (response.success) {
            location.reload();
          }
        },
      });
    }
  });

  // Delete chore
  $(".delete-chore").click(function () {
    const choreId = $(this).data("chore-id");
    if (confirm("Are you sure you want to delete this chore?")) {
      $.ajax({
        url: "/delete_chore",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ chore_id: choreId }),
        success: function (response) {
          if (response.success) {
            location.reload();
          }
        },
      });
    }
  });

  // View logs
  $('#view-logs').click(function() {
      $('#view-logs-modal').modal('show');
      loadLogs();
  });

  $('#log-date-range').daterangepicker({
      opens: 'left'
  }, function(start, end, label) {
      loadLogs(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
  });

  function loadLogs(startDate, endDate) {
      let url = '/get_logs';
      if (startDate && endDate) {
          url += `?start_date=${startDate}&end_date=${endDate}`;
      }
      $.get(url, function(data) {
          const logsContainer = $('#logs-container');
          logsContainer.empty();
          data.forEach(log => {
              logsContainer.append(`
                  <div class="log-entry">
                      <p class="mb-1"><strong>${log.horse_name}</strong>: ${log.chore_name}</p>
                      <p class="mb-0 log-timestamp">${new Date(log.timestamp).toLocaleString()}</p>
                  </div>
              `);
          });
      });
  }
  
  // Handle change password form submission
  $("#change-password-form").on("submit", function (e) {
    e.preventDefault();
    var newPassword = $("#new-password").val();

    $.ajax({
      url: "/change_password",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ new_password: newPassword }),
      success: function (response) {
        if (response.success) {
          alert("Password changed successfully");
          $("#new-password").val("");
        }
      },
    });
  });
});
