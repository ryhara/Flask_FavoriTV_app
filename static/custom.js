document.addEventListener('DOMContentLoaded', function() {
	var alertElement = document.getElementById('announce');

	if (alertElement) {
	  setTimeout(function() {
		alertElement.classList.add('fade');
		alertElement.classList.remove('show');

		setTimeout(function() {
		  alertElement.remove();
		}, 400);
	  }, 4000);
	}
});


function confirmDelete(elem) {
	if (confirm('Are you sure you want to delete this program?')) {
	  alert("Delete: " + elem);
	  document.getElementById("program_delete").value = "True";
	} else {
	  document.getElementById("program_delete").value = "False";
	  return 0;
	}
  }