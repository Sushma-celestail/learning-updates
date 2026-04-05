// ============================================
// MODAL COMPONENT (Default Export)
// ============================================

export default class Modal {

  constructor(message) {
    this.message = message;
  }

  // Create modal UI
  open() {

    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(0,0,0,0.5)";

    const box = document.createElement("div");
    box.style.background = "#fff";
    box.style.padding = "20px";
    box.style.margin = "100px auto";
    box.style.width = "200px";
    box.textContent = this.message;

    overlay.appendChild(box);
    document.body.appendChild(overlay);

    // Close on click
    overlay.onclick = () => overlay.remove();
  }
}