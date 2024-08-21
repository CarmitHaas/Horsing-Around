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

 $("#add-chore-form").on("submit", function (e) {
  e.preventDefault();
  var choreData = {
    name: $("#chore-name").val(),
    category: $("#chore-category").val(),
    assign_all: $("#assign-all-horses").is(":checked"),
    horse_ids: []
  };

  if (!choreData.assign_all) {
    $(".horse-checkbox:checked").each(function() {
      choreData.horse_ids.push($(this).val());
    });
  }

  $.ajax({
    url: "/add_chore",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(choreData),
    success: function (response) {
      if (response.success) {
        console.log("Chore added successfully:", response.chore);
        location.reload();
        if (choreData.assign_all) {
          $(".chore-list").each(function() {
            addChoreToUI($(this), response.chore);
          });
        } else {
          choreData.horse_ids.forEach(function(horseId) {
            addChoreToUI($(`#horse-${horseId} .chore-list`), response.chore);
          });
        }
        $("#add-chore-modal").modal("hide");
      }
    },
  });
});

function addChoreToUI(choreList, chore) {
  var categoryDiv = choreList.find(`.category-${chore.category}`);
  if (categoryDiv.length === 0) {
    categoryDiv = $(`<div class="mt-3 category category-${chore.category}">
                        <h6>${chore.category.replace('_', ' ').title()}</h6>
                     </div>`);
    choreList.append(categoryDiv);
  }
  
  var choreHtml = `
    <div class="form-check d-flex justify-content-between align-items-center">
      <div>
        <input type="checkbox" class="form-check-input chore-checkbox"
               id="chore-${chore._id}" data-horse-id="${choreList.closest('.card').data('horse-id')}"
               data-chore-id="${chore._id}">
        <label class="form-check-label" for="chore-${chore._id}">
          ${chore.name}
        </label>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-danger delete-chore"
                data-horse-id="${choreList.closest('.card').data('horse-id')}" data-chore-id="${chore._id}">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    </div>
  `;
  categoryDiv.append(choreHtml);
}

// Toggle specific horses selection based on "Assign to all horses" checkbox
$("#assign-all-horses").on("change", function() {
  $("#horse-checkboxes").toggle(!$(this).is(":checked"));
});

$('.edit-horse').click(function () {
  const horseId = $(this).data('horse-id');
  // Fetch horse data and populate the form
  $.ajax({
    url: `/get_horse/${horseId}`,
    method: 'GET',
    success: function (data) {
      $('#edit-horse-id').val(data._id);
      $('#edit-horse-name').val(data.name);
      $('#edit-horse-image').val(data.image);
      $('#edit-horse-info').val(data.info);
      $('#edit-horse-modal').modal('show');
    },
    error: function () {
      alert("Failed to fetch horse data.");
    }
  });
});

$('#edit-horse-form').submit(function (e) {
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
    success: function (response) {
      if (response.success) {
        location.reload();
      } else {
        alert("Failed to update horse.");
      }
    },
    error: function () {
      alert("An error occurred while updating the horse.");
    }
  });
});

  $(".delete-horse").on("click", function (event) {
    event.preventDefault();
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
          } else {
            alert("Failed to remove horse.");
          }
        },
        error: function () {
          alert("An error occurred while trying to remove the horse.");
        }
      });
    }
  });
});

$(document).on('click', '.delete-chore', function() {
  const horseId = $(this).data('horse-id');
  const choreId = $(this).data('chore-id');
  if (confirm("Are you sure you want to delete this chore?")) {
    $.ajax({
      url: "/remove_chore",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ horse_id: horseId, chore_id: choreId }),
      success: function(response) {
        if (response.success) {
          location.reload();
        } else {
          alert("Failed to delete chore.");
        }
      },
      error: function() {
        alert("An error occurred while deleting the chore.");
      }
    });
  }
});

$(document).on('click', '.edit-chore', function() {
  const horseId = $(this).data('horse-id');
  const choreId = $(this).data('chore-id');
  const choreName = $(this).closest('.form-check').find('.form-check-label').text().trim();
  const choreCategory = $(this).closest('.category').attr('class').split(' ').pop().replace('category-', '');
  
  const newName = prompt("Enter new chore name:", choreName);
  if (newName) {
    const newCategory = prompt("Enter new category (day_opening, pre_lesson, post_lesson, end_of_day):", choreCategory);
    if (newCategory) {
      $.ajax({
        url: "/edit_chore",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
          horse_id: horseId,
          chore_id: choreId,
          updated_data: { name: newName, category: newCategory }
        }),
        success: function(response) {
          if (response.success) {
            location.reload();
          } else {
            alert("Failed to update chore.");
          }
        },
        error: function() {
          alert("An error occurred while updating the chore.");
        }
      });
    }
  }
});
// // Handle remove chore
// $(".remove-chore").on("click", function () {
//   var choreId = $(this).data("chore-id");
//   if (confirm("Are you sure you want to remove this chore?")) {
//     $.ajax({
//       url: "/remove_chore",
//       method: "POST",
//       contentType: "application/json",
//       data: JSON.stringify({ chore_id: choreId }),
//       success: function (response) {
//         if (response.success) {
//           location.reload();
//         }
//       },
//     });
//   }
// });

// $("#add-chore-form").on("submit", function (e) {
//   e.preventDefault();
//   var choreData = {
//     name: $("#chore-name").val(),
//     category: $("#chore-category").val(),
//   };

//   $.ajax({
//     url: "/add_chore",
//     method: "POST",
//     contentType: "application/json",
//     data: JSON.stringify(choreData),
//     success: function (response) {
//       if (response.success) {
//         location.reload();
//       }
//     },
//   });
// });

// // Delete chore
// $(".delete-chore").click(function () {
//   const choreId = $(this).data("chore-id");
//   if (confirm("Are you sure you want to delete this chore?")) {
//     $.ajax({
//       url: "/delete_chore",
//       method: "POST",
//       contentType: "application/json",
//       data: JSON.stringify({ chore_id: choreId }),
//       success: function (response) {
//         if (response.success) {
//           location.reload();
//         }
//       },
//     });
//   }
// });

// View logs
$('#view-logs').click(function () {
  $('#view-logs-modal').modal('show');
  loadLogs();
});

$('#log-date-range').daterangepicker({
  opens: 'left'
}, function (start, end, label) {
  loadLogs(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
});

function loadLogs(startDate, endDate) {
  let url = '/get_logs';
  if (startDate && endDate) {
    url += `?start_date=${startDate}&end_date=${endDate}`;
  }
  $.get(url, function (data) {
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

