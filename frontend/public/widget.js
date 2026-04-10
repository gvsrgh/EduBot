/**
 * EduBot+ Embeddable Widget Loader
 *
 * Usage:
 *   <script src="https://YOUR_FRONTEND_DOMAIN/widget.js" data-bot="edubot"></script>
 *
 * Optional attributes:
 *   data-greeting  — custom greeting text
 *   data-position  — "bottom-right" (default) or "bottom-left"
 *   data-color     — accent colour hex (default "#2563eb")
 */
(function () {
  "use strict";

  // Prevent double-init
  if (window.__edubot_widget_loaded) return;
  window.__edubot_widget_loaded = true;

  // ── Read config from script tag ──────────────────────────────
  var script =
    document.currentScript ||
    document.querySelector('script[data-bot="edubot"]');
  if (!script) return;

  var baseUrl = new URL(script.src).origin; // frontend origin
  var greeting = script.getAttribute("data-greeting") || "";
  var position = script.getAttribute("data-position") || "bottom-right";
  var color = script.getAttribute("data-color") || "#2563eb";

  // ── Styles (scoped via unique prefix) ────────────────────────
  var CSS =
    "#edubot-widget-launcher{" +
    "position:fixed;" +
    (position === "bottom-left" ? "left:20px;" : "right:20px;") +
    "bottom:60px;" +
    "width:56px;height:56px;border-radius:50%;" +
    "background:" + color + ";" +
    "color:#fff;border:none;cursor:pointer;" +
    "box-shadow:0 4px 14px rgba(0,0,0,.25);" +
    "z-index:2147483646;" +
    "display:flex;align-items:center;justify-content:center;" +
    "transition:transform .2s,box-shadow .2s;" +
    "font-family:system-ui,sans-serif;" +
    "}" +
    "#edubot-widget-launcher:hover{transform:scale(1.08);box-shadow:0 6px 20px rgba(0,0,0,.3);}" +
    "#edubot-widget-frame{" +
    "position:fixed;" +
    (position === "bottom-left" ? "left:20px;" : "right:20px;") +
    "bottom:128px;" +
    "width:380px;height:520px;" +
    "max-width:calc(100vw - 40px);max-height:calc(100vh - 148px);" +
    "border:none;border-radius:12px;" +
    "box-shadow:0 8px 30px rgba(0,0,0,.2);" +
    "z-index:2147483647;" +
    "display:none;" +
    "background:#fff;" +
    "}" +
    "@media(max-width:480px){" +
    "#edubot-widget-frame{" +
    "width:100vw;height:100vh;" +
    "max-width:100vw;max-height:100vh;" +
    "top:0;left:0;right:0;bottom:0;" +
    "border-radius:0;" +
    "}" +
    "}";

  var style = document.createElement("style");
  style.textContent = CSS;
  document.head.appendChild(style);

  // ── Launcher button ──────────────────────────────────────────
  var btn = document.createElement("button");
  btn.id = "edubot-widget-launcher";
  btn.setAttribute("aria-label", "Open chat");
  btn.innerHTML =
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>' +
    "</svg>";
  document.body.appendChild(btn);

  // ── Chat iframe ──────────────────────────────────────────────
  var iframe = document.createElement("iframe");
  iframe.id = "edubot-widget-frame";
  iframe.title = "EduBot+ Chat";
  iframe.allow = "clipboard-write";
  var params = "?embed=1";
  if (greeting) params += "&greeting=" + encodeURIComponent(greeting);
  if (color) params += "&color=" + encodeURIComponent(color);
  iframe.src = baseUrl + "/widget" + params;
  document.body.appendChild(iframe);

  // ── Toggle logic ─────────────────────────────────────────────
  var open = false;

  function toggle() {
    open = !open;
    iframe.style.display = open ? "block" : "none";
    btn.innerHTML = open
      ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
      : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>';
    btn.setAttribute("aria-label", open ? "Close chat" : "Open chat");
  }

  btn.addEventListener("click", toggle);

  // Listen for close messages from the iframe
  window.addEventListener("message", function (e) {
    if (e.origin !== baseUrl) return;
    if (e.data === "edubot-widget-close" && open) toggle();
  });
})();
