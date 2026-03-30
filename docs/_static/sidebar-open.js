document.addEventListener("DOMContentLoaded", function () {
  var toggles = document.querySelectorAll(".sidebar-tree input.toctree-checkbox");
  toggles.forEach(function (toggle) {
    toggle.checked = true;
  });

  var tables = document.querySelectorAll(".table-wrapper > table.docutils");
  tables.forEach(function (table) {
    var caption = table.querySelector(":scope > caption");
    if (!caption) {
      return;
    }

    var wrapper = table.parentElement;
    if (!wrapper || wrapper.querySelector(":scope > .table-caption")) {
      return;
    }

    var captionBlock = document.createElement("div");
    captionBlock.className = "table-caption";

    while (caption.firstChild) {
      captionBlock.appendChild(caption.firstChild);
    }

    if (table.id) {
      captionBlock.id = table.id + "-caption";
      table.setAttribute("aria-describedby", captionBlock.id);
    }

    wrapper.insertBefore(captionBlock, table.nextSibling);
    caption.remove();
  });
});
