document.addEventListener("DOMContentLoaded", function () {
  var toggles = document.querySelectorAll(".sidebar-tree input.toctree-checkbox");
  toggles.forEach(function (toggle) {
    toggle.checked = true;
  });
});
