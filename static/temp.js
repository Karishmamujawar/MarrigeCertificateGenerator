
function toggleTemplates(id) {
    const btnGroup = document.getElementById(`template-btns-${id}`);
    if (btnGroup.style.display === "none") {
        btnGroup.style.display = "block";
    } else {
        btnGroup.style.display = "none";
    }
}


  function confirmDelete() {
    return confirm("Are you sure you want to delete this certificate?");
  }