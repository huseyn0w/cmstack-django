// Admin-only bundle: the Trix rich-text editor. Loaded only by dashboard pages,
// so the public site stays lean. Editor output is HTML and is sanitized
// server-side with nh3 on save (apps/content), so this stays a pure UI concern.
import "trix";
import "trix/dist/trix.css";
import "./admin.css";

// Media picker → Trix. The picker modal (dashboard/_media_picker.html) calls this
// to drop a library image into the active editor. Output is sanitized server-side
// (nh3 allows img src/alt), so inserting raw HTML here is safe.
window.cmstackInsertImage = function (url, alt) {
  const editor = document.querySelector("trix-editor");
  if (!editor || !editor.editor) return;
  const safeAlt = (alt || "").replace(/"/g, "&quot;");
  editor.editor.insertHTML(`<img src="${url}" alt="${safeAlt}">`);
};
