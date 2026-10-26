/* SmartBrew AI browser client. No external libraries or live AI service are used. */
"use strict";

const state = {
  view: "brew", adminTab: "menu", menu: {products: [], machine_mode: "normal"},
  session: {role: null, machine_mode: "normal"}, category: "all", search: "",
  selected: null, milk: 40, sugar: 0, payment: "card", paymentResult: "approved",
  scenario: "mild", hour: new Date().getUTCHours(), weather: null, recommendation: null,
  order: null, inventory: null, dashboard: null, logs: [], diagnostics: {}, busy: false,
};
const main = document.querySelector("#main");
const dialog = document.querySelector("#dialog");
let toastTimer;
let polling = false;

/** Escape untrusted API text for HTML insertion. Input: any value. Output: safe string. */
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, escapeCharacter);
}
/** Map one HTML-sensitive character to its entity. Input: character. Output: entity string. */
function escapeCharacter(character) {
  return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[character];
}
/** Format integer cents in USD. Input: cents. Output: currency string. */
function money(cents) {
  return new Intl.NumberFormat("en-US", {style: "currency", currency: "USD"}).format(Number(cents) / 100);
}
/** Format a server timestamp for the browser's local zone. Input: ISO timestamp. Output: string. */
function timestamp(value) {
  return new Date(value).toLocaleString("en-GB", {month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"});
}
/** Call the same-origin JSON API. Inputs: path, optional method/body. Output: parsed JSON; throws on failure. */
async function api(path, method = "GET", body) {
  const options = {method, credentials: "same-origin", headers: {"Accept": "application/json"}};
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
  return data;
}
/** Announce a short result accessibly. Inputs: message, optional error flag. Output: none. */
function notify(message, error = false) {
  const element = document.querySelector("#toast");
  element.textContent = message;
  element.className = `toast${error ? " error" : ""}`;
  element.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(hideToast, 6500);
}
/** Hide the current notification. Input: none. Output: none. */
function hideToast() {
  document.querySelector("#toast").hidden = true;
}
/** Persist only the public opaque order ID. Input: ID or null. Output: none; storage errors are nonfatal. */
function saveOrderID(id) {
  try {
    if (id) localStorage.setItem("smartbrew.order", id);
    else localStorage.removeItem("smartbrew.order");
  } catch (error) {
    notify("Browser storage is unavailable; keep this page open to track your drink.");
  }
}
/** Restore the last public order ID. Input: none. Output: string or null. */
function savedOrderID() {
  try { return localStorage.getItem("smartbrew.order"); }
  catch (error) { return null; }
}
/** Make initial API requests and restore an unfinished order. Input: none. Output: Promise<void>. */
async function initialize() {
  try {
    const results = await Promise.all([api("/api/menu"), api("/api/session"), api(`/api/weather?scenario=${state.scenario}&hour=${state.hour}`)]);
    [state.menu, state.session, state.weather] = results;
    const id = savedOrderID();
    if (id) {
      try { state.order = await api(`/api/orders/${encodeURIComponent(id)}`); }
      catch (error) { saveOrderID(null); }
    }
    render();
  } catch (error) {
    main.innerHTML = `<div class="notice error"><h2>We couldn’t connect to the coffee machine.</h2><p>${escapeHTML(error.message)}</p><button class="btn" data-action="retry">Try again</button></div>`;
  }
}
/** Render the selected page and navigation state. Input: none. Output: none. */
function render() {
  for (const button of document.querySelectorAll("[data-view]")) {
    const active = button.dataset.view === state.view;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  }
  const captions = {brew: "Brew coffee", admin: "Administration", service: "Machine service", insights: "Sales insights"};
  document.querySelector("#page-caption").textContent = captions[state.view];
  document.querySelector("#machine-label").textContent = state.session.machine_mode === "service" ? "Service mode active" : "Machine connected";
  if (state.view === "brew") renderBrew();
  else if ((state.view === "admin" || state.view === "insights") && state.session.role !== "admin") renderLogin("admin");
  else if (state.view === "service" && state.session.role !== "technician") renderLogin("technician");
  else if (state.view === "admin") renderAdmin();
  else if (state.view === "service") renderService();
  else renderInsights();
  applyBarWidths(main);
}
/** Apply validated chart widths through CSSOM, compatible with the strict CSP. Input: root element. Output: none. */
function applyBarWidths(root) {
  for (const element of root.querySelectorAll("[data-bar-width]")) {
    const width = Math.max(0, Math.min(100, Number(element.dataset.barWidth) || 0));
    element.style.width = `${width}%`;
  }
}
/** Return a page heading. Inputs: eyebrow, title, description, optional badge. Output: safe HTML. */
function heading(eyebrow, title, description, badge = "") {
  return `<div class="page-heading"><div><div class="eyebrow">${escapeHTML(eyebrow)}</div><h1>${escapeHTML(title)}</h1><p class="subtext">${escapeHTML(description)}</p></div>${badge}</div>`;
}
/** Render the coffee menu, suggestions and checkout/progress panel. Input: none. Output: none. */
function renderBrew() {
  const machineNotice = state.session.machine_mode === "service" ? '<div class="notice warn">The machine is in service mode. Please wait for the technician to finish before ordering.</div>' : "";
  main.innerHTML = `${heading("A SMALL MOMENT, JUST FOR YOU", "Your next great coffee.", "Choose your favorite. Make it yours. We’ll take care of the rest.", '<span class="date-chip">● &nbsp; Fresh beans daily</span>')}${machineNotice}
    <section class="hero" aria-label="Welcome"><div><div class="eyebrow">CRAFTED AROUND YOUR DAY</div><h2>A little pause.<br>A perfectly personal cup.</h2><p>From the first sip to the last, your coffee should feel like you. Let’s find your blend.</p></div><div class="hero-visual" aria-hidden="true"><span class="hero-star">✧</span><div class="coffee-disc"><div class="cup-top"></div></div></div></section>
    <div class="brew-layout"><section aria-labelledby="menu-heading"><div class="section-heading"><h2 id="menu-heading">The coffee collection <span class="count">${state.menu.products.length} drinks</span></h2></div><div class="filter-bar"><div class="chips" aria-label="Drink temperature"><button class="chip ${state.category === "all" ? "active" : ""}" data-category="all">All drinks</button><button class="chip ${state.category === "hot" ? "active" : ""}" data-category="hot">Hot</button><button class="chip ${state.category === "iced" ? "active" : ""}" data-category="iced">Iced</button></div><input class="search" id="search" type="search" placeholder="Search the menu…" aria-label="Search drinks" value="${escapeHTML(state.search)}"></div><div id="products" class="product-grid"></div><p class="readonly-note">Allergy notice: milk-containing drinks use a shared machine. Ingredient availability is checked again before payment.</p></section><aside class="brew-aside"><div id="order-panel"></div><div id="recommendation-panel"></div></aside></div>`;
  renderProducts();
  renderOrderPanel();
  renderRecommendation();
}
/** Render products matching current search/filter without disturbing input focus. Input: none. Output: none. */
function renderProducts() {
  const matches = state.menu.products.filter(productMatches);
  document.querySelector("#products").innerHTML = matches.length ? matches.map(productCard).join("") : '<div class="empty-state">No drinks found. Try another search.</div>';
}
/** Test a product against filters. Input: product. Output: boolean. */
function productMatches(product) {
  return (state.category === "all" || product.category === state.category) && `${product.name} ${product.description}`.toLowerCase().includes(state.search.toLowerCase());
}
/** Build one coffee card. Input: product object. Output: safe HTML. */
function productCard(product) {
  return `<article class="product-card"><div class="product-art ${product.category === "iced" ? "iced" : "hot"}" aria-hidden="true"><span class="art-label">${product.category === "iced" ? "OVER ICE" : "FRESHLY BREWED"}</span><span class="drink-cup"></span></div><div class="product-meta"><h3>${escapeHTML(product.name)}</h3><p>${escapeHTML(product.description)}</p><div class="product-bottom"><span class="price">${money(product.price_cents)}</span>${product.available ? `<button class="circle-button" data-select="${escapeHTML(product.id)}" aria-label="Customize ${escapeHTML(product.name)}">+</button>` : '<span class="badge neutral">Unavailable</span>'}</div></div></article>`;
}
/** Render custom recipe, payment simulator, or active order into the side panel. Input: none. Output: none. */
function renderOrderPanel() {
  const target = document.querySelector("#order-panel");
  if (!target) return;
  if (state.order) { target.innerHTML = orderPanel(); applyBarWidths(target); return; }
  const product = state.menu.products.find(isSelected);
  if (!product) {
    target.innerHTML = '<section class="panel customization-card"><div class="panel-title"><h2>Your perfect cup</h2><span class="tiny-icon">♧</span></div><div class="empty-order"><div class="empty-order-icon" aria-hidden="true">☕</div><h3>Start with a favorite.</h3><p>Select a drink from the collection<br>to create your own coffee moment.</p></div><div class="divider"></div><p class="fine-print">Your recipe. Your rhythm.<br>Customize milk and sugar with a simple slide.</p></section>';
    return;
  }
  target.innerHTML = `<section class="panel customization-card"><div class="panel-title"><h2>Make it yours</h2><button class="text-button" data-action="clear-selection">Change drink</button></div><h3 class="selected-name">${escapeHTML(product.name)}</h3><p class="selected-description">${escapeHTML(product.description)}</p><form id="checkout-form"><div class="field"><label class="range-label" for="milk">Milk <output id="milk-value" for="milk">${state.milk}%</output></label><input type="range" id="milk" name="milk" min="0" max="100" value="${state.milk}"><div class="range-limits"><span>No milk</span><span>Extra creamy</span></div></div><div class="field"><label class="range-label" for="sugar">Sugar <output id="sugar-value" for="sugar">${state.sugar} g</output></label><input type="range" id="sugar" name="sugar" min="0" max="20" value="${state.sugar}"><div class="range-limits"><span>Unsweetened</span><span>20 g</span></div></div><div class="recipe-preview" id="recipe-preview">${recipeText()}</div><div class="total-row"><span>Your total</span><strong>${money(product.price_cents)}</strong></div><div class="payment-options"><label class="payment-choice"><input type="radio" name="payment" value="card" ${state.payment === "card" ? "checked" : ""}> ▣ Card</label><label class="payment-choice"><input type="radio" name="payment" value="phone" ${state.payment === "phone" ? "checked" : ""}> ▯ Phone</label></div><label class="field simulator-field">Demo payment response<select id="payment-result" name="payment_result"><option value="approved" ${state.paymentResult === "approved" ? "selected" : ""}>Approved · simulation</option><option value="declined" ${state.paymentResult === "declined" ? "selected" : ""}>Declined · simulation</option></select></label><button class="btn full" type="submit" ${state.session.machine_mode === "service" || state.busy ? "disabled" : ""}>${state.busy ? "Processing…" : "Pay & brew"} <span aria-hidden="true">→</span></button><p class="fine-print">No real payment is taken. Brewing is simulated for this classroom prototype.</p></form></section>`;
}
/** Test whether a product is selected. Input: product. Output: boolean. */
function isSelected(product) { return String(product.id) === String(state.selected); }
/** Describe the current recipe. Input: none. Output: escaped HTML text. */
function recipeText() { return `${state.milk}% milk · ${state.sugar ? `${state.sugar} g sugar` : "No added sugar"} · Freshly prepared`; }
/** Build active order progress and collection controls. Input: none. Output: safe HTML. */
function orderPanel() {
  const order = state.order;
  const ready = order.status === "ready";
  const completed = order.status === "completed";
  const progress = Math.max(0, Math.min(100, Number(order.progress) || 0));
  return `<section class="panel"><div class="panel-title"><h2>Your coffee moment</h2><span class="badge">${completed ? "Collected" : ready ? "Ready" : "Brewing"}</span></div>${ready || completed ? '<div class="ready-icon" aria-hidden="true">✓</div>' : ""}<h3 class="order-status">${completed ? "Enjoy every sip." : ready ? "Made just for you." : "Good things are brewing."}</h3><p class="subtext">${completed ? "Thanks for making us part of your day." : ready ? "Your coffee is ready. Collect it below." : "Your payment was approved. Your cup is on its way."}</p><div class="order-id">${escapeHTML(order.id)}</div><div class="progress-track" role="progressbar" aria-label="Coffee brewing progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}"><div class="progress-fill" data-bar-width="${progress}"></div></div><div class="progress-meta"><span>${completed ? "Collected" : ready ? "Ready to collect" : "Preparing your recipe"}</span><span>${progress}%</span></div><div class="order-summary"><strong>${escapeHTML(order.product_name)}</strong><br>${escapeHTML(order.milk_percent)}% milk · ${escapeHTML(order.sugar_grams)} g sugar<br>${money(order.total_cents)} · ${escapeHTML(order.payment_method)} payment</div>${ready ? '<button class="btn full" data-action="collect">Collect my coffee →</button>' : completed ? '<button class="btn full" data-action="new-drink">Find your next favorite →</button>' : '<p class="fine-print">Simulated preparation takes about 12 seconds. Keep this page open or return on the same browser.</p>'}</section>`;
}
/** Build weather and deterministic suggestion controls. Input: none. Output: none. */
function renderRecommendation() {
  const target = document.querySelector("#recommendation-panel");
  if (!target) return;
  const weather = state.weather;
  target.innerHTML = `<section class="panel recommendation"><div class="eyebrow">A LITTLE INSPIRATION</div><h2>Let your day<br>choose your coffee.</h2><p class="subtext">A suggestion for the weather and your rhythm.</p><div class="weather-line"><span class="weather-icon" aria-hidden="true">${state.scenario === "hot" ? "☀" : state.scenario === "cold" ? "❄" : state.scenario === "offline" ? "◌" : "☁"}</span><span>${weather ? weather.online ? `${escapeHTML(weather.temperature_c)}°C · ${escapeHTML(weather.condition)}` : "Weather offline · time-based fallback" : "Loading weather…"}</span></div><div class="weather-controls"><label><span class="fine-print">Weather simulation</span><select id="weather-scenario" aria-label="Simulated weather scenario"><option value="mild" ${state.scenario === "mild" ? "selected" : ""}>Mild day</option><option value="hot" ${state.scenario === "hot" ? "selected" : ""}>Hot · 30°C</option><option value="cold" ${state.scenario === "cold" ? "selected" : ""}>Cold day</option><option value="offline" ${state.scenario === "offline" ? "selected" : ""}>Offline</option></select></label><label><span class="fine-print">UTC hour</span><input id="weather-hour" type="number" min="0" max="23" value="${state.hour}" aria-label="Simulated UTC hour from 0 to 23"></label></div><button class="btn secondary full" data-action="recommend">✧ &nbsp; Surprise me</button>${state.recommendation ? `<div class="divider"></div><h3>${escapeHTML(state.recommendation.product_name)}</h3><p class="subtext">${escapeHTML(state.recommendation.reason)}</p>` : ""}<p class="fine-print">Transparent by design: this prototype uses deterministic rules and simulated weather, not a live AI model or weather API.</p></section>`;
}
/** Render role-specific login with openly disclosed demonstration credentials. Input: role. Output: none. */
function renderLogin(role) {
  const tech = role === "technician";
  main.innerHTML = `${heading(tech ? "CARE BEHIND EVERY CUP" : "BEHIND THE COUNTER", tech ? "Keep good coffee flowing." : "A thoughtfully managed machine.", tech ? "A dedicated space for safe diagnostics and maintenance." : "Manage the menu, monitor ingredients, and make informed decisions.")}
    <div class="auth-layout"><section class="panel auth-card"><div class="eyebrow">${tech ? "MAINTENANCE TECHNICIAN" : "SYSTEM ADMINISTRATOR"}</div><h2>${tech ? "Technician access" : "Welcome back."}</h2><p class="subtext">${tech ? "Enter your maintenance PIN to access service tools." : "Sign in to your machine’s administration workspace."}</p><div class="divider"></div><form id="login-form" data-role="${role}"><label class="field"><span>${tech ? "Maintenance PIN" : "Admin password"}</span><input name="credential" type="password" autocomplete="current-password" ${tech ? 'inputmode="numeric"' : ""} required maxlength="128" placeholder="${tech ? "Enter PIN" : "Enter your password"}"></label><button class="btn full" type="submit">${tech ? "Access service workspace" : "Sign in to administration"} →</button></form><p class="fine-print">Classroom demo credential: <strong>${tech ? "2468" : "smartbrew-admin"}</strong>. These disclosed credentials demonstrate role-based access and must be replaced for production.</p></section><section class="auth-visual"><div class="eyebrow">${tech ? "DIAGNOSE. UNDERSTAND. RESTORE." : "THE DETAILS MAKE THE DIFFERENCE."}</div><h2>${tech ? "A little care.<br>A better everyday." : "Great coffee starts<br>behind the scenes."}</h2><p>${tech ? "Service mode pauses customer ordering so simulated pump and heater tests can run safely. Error logs can be exported as CSV." : "Fresh ingredients. A considered menu. Clear daily reporting. Everything you need, all in one place."}</p></section></div>`;
}
/** Return the current role/session toolbar. Input: role label. Output: safe HTML. */
function sessionBar(label) {
  return `<div class="session-bar"><span>● &nbsp; Signed in as <strong>${escapeHTML(label)}</strong> · Demo account</span><button class="text-button" data-action="logout">Sign out</button></div>`;
}
/** Load page-specific protected data after navigation or mutation. Input: none. Output: Promise<void>. */
async function refreshProtected() {
  if (state.view === "admin" && state.session.role === "admin") {
    const results = await Promise.all([api("/api/admin/menu"), api("/api/inventory")]);
    state.adminMenu = results[0]; state.inventory = results[1];
  } else if (state.view === "service" && state.session.role === "technician") {
    state.logs = (await api("/api/service/logs")).logs;
  } else if (state.view === "insights" && state.session.role === "admin") {
    state.dashboard = await api("/api/dashboard");
  }
}
/** Switch page and fetch its current data. Input: view key. Output: Promise<void>. */
async function navigate(view) {
  state.view = view;
  if (view === "brew") {
    [state.menu, state.session] = await Promise.all([api("/api/menu"), api("/api/session")]);
  } else await refreshProtected();
  render();
}
/** Render menu management or sensor inventory. Input: none. Output: none. */
function renderAdmin() {
  main.innerHTML = `${heading("THE DETAILS BEHIND THE BREW", "Your machine, at a glance.", "A fresh menu and a well-stocked machine make every cup a better one.")}${sessionBar("System administrator")}<div class="tabs"><button class="btn ${state.adminTab === "menu" ? "" : "light"}" data-admin-tab="menu">▦ &nbsp; Menu editor</button><button class="btn ${state.adminTab === "inventory" ? "" : "light"}" data-admin-tab="inventory">◒ &nbsp; Ingredients & alerts</button></div>${state.adminTab === "menu" ? menuEditor() : inventoryPanel()}`;
}
/** Build the administrator menu table and product creation instructions. Input: none. Output: safe HTML. */
function menuEditor() {
  const products = state.adminMenu?.products || [];
  return `<div class="admin-columns"><section class="panel"><div class="section-heading"><h2>The current collection</h2><button class="btn small" data-action="add-product">+ Add drink</button></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Drink</th><th>Price</th><th>Status</th><th>Action</th></tr></thead><tbody>${products.map(adminProductRow).join("")}</tbody></table></div></section><aside class="panel recommendation"><div class="eyebrow">CURATE YOUR COLLECTION</div><h2>A menu that<br>moves with you.</h2><p class="subtext">Add a new favorite, refine a recipe, or pause a drink. Published changes appear immediately on the customer menu.</p><div class="divider"></div><p class="fine-print">Demo note: new drinks use the machine’s standard coffee recipe. A name such as “Matcha Latte” does not add matcha hardware or ingredients.</p></aside></div>`;
}
/** Build one editable product table row. Input: product. Output: safe HTML. */
function adminProductRow(product) {
  return `<tr><td><strong>${escapeHTML(product.name)}</strong><span class="secondary-text">${escapeHTML(product.category)} · ${escapeHTML(product.default_milk_percent)}% milk</span></td><td>${money(product.price_cents)}</td><td><span class="badge ${product.active ? "" : "neutral"}">${product.active ? "Active" : "Paused"}</span></td><td><button class="btn small light" data-edit="${escapeHTML(product.id)}">Edit</button></td></tr>`;
}
/** Render stock percentages and strict below-15% alerts. Input: none. Output: safe HTML. */
function inventoryPanel() {
  if (!state.inventory) return '<div class="empty-state">Inventory unavailable. Refresh to try again.</div>';
  const alerts = state.inventory.alerts || [];
  return `${alerts.length ? `<div class="notice warn"><strong>${alerts.length} ingredient${alerts.length > 1 ? "s" : ""} need attention.</strong> ${alerts.map(ingredientName).map(escapeHTML).join(", ")} below the 15% threshold.</div>` : '<div class="notice">All ingredient levels are healthy. Alerts trigger strictly below 15% of capacity.</div>'}<div class="section-heading"><h2>Ingredient levels</h2><button class="btn small light" data-action="refresh">↻ Refresh</button></div><div class="stock-grid">${state.inventory.ingredients.map(stockCard).join("")}</div><div class="notice"><strong>Simulated sensor readings.</strong> Use “Set level” to demonstrate a refill or low-stock condition. Values are persisted in SQLite; there are no physical ingredient sensors in this prototype.</div>`;
}
/** Select an ingredient name. Input: ingredient. Output: name string. */
function ingredientName(ingredient) { return ingredient.name; }
/** Build an ingredient stock card. Input: ingredient object. Output: safe HTML. */
function stockCard(ingredient) {
  const percentage = Math.max(0, Math.min(100, Number(ingredient.percentage) || 0));
  return `<article class="stock-card ${ingredient.low ? "low" : ""}"><h3>${escapeHTML(ingredient.name)}</h3><div class="stock-number">${escapeHTML(ingredient.stock)} <small>/ ${escapeHTML(ingredient.capacity)} ${escapeHTML(ingredient.unit)}</small></div><div class="stock-bar"><span data-bar-width="${percentage}"></span></div><div class="stock-bottom"><span>${percentage.toFixed(1)}% · ${ingredient.low ? "Low stock" : "Healthy"}</span><button class="text-button" data-stock="${escapeHTML(ingredient.id)}">Set level</button></div></article>`;
}
/** Render maintenance mode, simulated diagnostics and error log export. Input: none. Output: none. */
function renderService() {
  const enabled = state.session.machine_mode === "service";
  main.innerHTML = `${heading("CARE BEHIND EVERY CUP", "A little care goes a long way.", "Inspect, diagnose, and keep the machine ready for its next coffee moment.")}${sessionBar("Maintenance technician")}<section class="panel"><div class="section-heading"><div><h2>Service mode <span class="badge ${enabled ? "warn" : "neutral"}">${enabled ? "Enabled" : "Disabled"}</span></h2><p class="subtext">${enabled ? "Customer ordering is paused while you work." : "Enable service mode before running diagnostics."}</p></div><button class="btn ${enabled ? "secondary" : ""}" data-action="toggle-service">${enabled ? "Finish maintenance" : "Enable service mode"}</button></div><p class="fine-print">Service mode cannot start while a drink is brewing or waiting for collection. Signing out does not change the machine mode.</p></section><div class="section-heading"><h2>Component diagnostics</h2><span class="badge neutral">SIMULATED HARDWARE</span></div><div class="component-grid">${["milk_pump", "water_pump", "heater"].map(componentCard).join("")}</div><section class="panel"><div class="section-heading"><div><h2>Machine event log</h2><p class="subtext">A clear record of diagnostics, alerts, and system events.</p></div><div class="inline-actions"><button class="btn small light" data-action="refresh">↻ Refresh</button><a class="btn small" href="/api/service/logs.csv" download="smartbrew-logs.csv">↓ Export CSV</a></div></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Time</th><th>Level</th><th>Event</th><th>Details</th></tr></thead><tbody>${state.logs.length ? state.logs.map(logRow).join("") : '<tr><td colspan="4">No events yet. Run a diagnostic to add an entry.</td></tr>'}</tbody></table></div><p class="fine-print">Export downloads a CSV file through your browser. To store it on a USB drive, choose that drive in your browser’s save dialog or copy the downloaded file. The browser does not directly access USB hardware.</p></section>`;
}
/** Build one simulated diagnostic card. Input: component identifier. Output: safe HTML. */
function componentCard(component) {
  const labels = {milk_pump: "Milk pump", water_pump: "Water pump", heater: "Heating element"};
  const descriptions = {milk_pump: "Check the simulated milk delivery flow.", water_pump: "Verify simulated water circulation.", heater: "Inspect the simulated brewing temperature."};
  const result = state.diagnostics[component];
  return `<article class="component-card"><div class="component-icon" aria-hidden="true">${component === "heater" ? "♨" : "◒"}</div><h3>${labels[component]}</h3><p>${descriptions[component]}</p><form class="diagnostic-form" data-component="${component}"><label class="checkbox-field"><input type="checkbox" name="simulate_fault"> Simulate component fault</label><button class="btn secondary full" type="submit" ${state.session.machine_mode !== "service" || state.busy ? "disabled" : ""}>${state.busy ? "Testing…" : "Simulate 2 s test"}</button></form>${result ? `<div class="diagnostic-result ${result.passed ? "" : "failed"}"><strong>${result.passed ? "✓ Test passed" : "! Fault detected"}</strong><br>${escapeHTML(result.reading)} ${escapeHTML(result.unit)} · ${escapeHTML(result.duration_seconds)} s nominal<br><span class="fine-print">Simulation · ${timestamp(result.created_at)}</span></div>` : ""}</article>`;
}
/** Build one audit log row. Input: log object. Output: safe HTML. */
function logRow(log) {
  return `<tr><td class="mono">${escapeHTML(timestamp(log.created_at))}</td><td><span class="badge ${log.severity === "error" ? "bad" : log.severity === "warning" ? "warn" : "neutral"}">${escapeHTML(log.severity)}</span></td><td>${escapeHTML(log.event)}</td><td>${escapeHTML(log.message)}</td></tr>`;
}
/** Render daily sales metrics and popularity. Input: none. Output: none. */
function renderInsights() {
  const data = state.dashboard;
  if (!data) { main.innerHTML = '<div class="empty-state">Report unavailable. Choose this page again to refresh.</div>'; return; }
  const max = Math.max(1, ...data.popular_products.map(productQuantity));
  main.innerHTML = `${heading("A CLEARER PICTURE", "Every cup tells a story.", "Daily sales, customer favorites, and the ingredients that keep you going.", `<span class="date-chip">${escapeHTML(data.date)} · UTC</span>`)}${sessionBar("System administrator")}<div class="section-heading"><h2>Today’s performance</h2><button class="btn small light" data-action="refresh">↻ Refresh</button></div><div class="metric-grid"><article class="metric"><div class="metric-label">DAILY REVENUE</div><div class="metric-value">${money(data.revenue_cents)}</div><div class="metric-caption">Collected orders only</div></article><article class="metric"><div class="metric-label">PAID ORDERS</div><div class="metric-value">${escapeHTML(data.total_orders)}</div><div class="metric-caption">Declined payments excluded</div></article><article class="metric"><div class="metric-label">COLLECTED CUPS</div><div class="metric-value">${escapeHTML(data.completed_orders)}</div><div class="metric-caption">Brewed and collected</div></article><article class="metric"><div class="metric-label">AVERAGE ORDER</div><div class="metric-value">${money(data.average_order_cents)}</div><div class="metric-caption">Per collected order</div></article></div><div class="report-columns"><section class="panel"><div class="panel-title"><h2>Today’s favorites</h2><span class="tiny-icon">↗</span></div>${data.popular_products.length ? data.popular_products.map(popularityRow.bind(null, max)).join("") : '<div class="empty-state"><span class="empty-symbol">☕</span>The first cup is still to come.<br>Collected orders will appear here.</div>'}</section><section class="panel"><div class="panel-title"><h2>Ingredient watch</h2><span class="badge ${data.low_stock.length ? "warn" : ""}">${data.low_stock.length ? `${data.low_stock.length} low` : "All healthy"}</span></div>${data.low_stock.length ? data.low_stock.map(lowStockRow).join("") : '<p class="subtext">Every ingredient is at or above the 15% threshold. Your next coffee moment is in good hands.</p>'}<div class="divider"></div><button class="btn secondary full" data-view="admin" data-open-inventory="true">View ingredient levels →</button></section></div><p class="readonly-note">Reports use the server’s UTC calendar day. Revenue, popularity, and average order value include collected drinks only; paid orders also include drinks still in progress. Figures reflect prototype data only.</p>`;
}
/** Read a product's quantity for chart scaling. Input: product summary. Output: number. */
function productQuantity(product) { return Number(product.quantity); }
/** Build one relative popularity bar. Inputs: maximum quantity, product summary. Output: safe HTML. */
function popularityRow(max, product) {
  const width = Math.max(0, Math.min(100, product.quantity / max * 100));
  return `<div class="popularity-row"><span>${escapeHTML(product.name)}</span><div class="popularity-track"><span data-bar-width="${width}"></span></div><strong>${escapeHTML(product.quantity)}</strong></div>`;
}
/** Build one low-stock summary. Input: ingredient. Output: safe HTML. */
function lowStockRow(ingredient) {
  return `<div class="total-row"><span>${escapeHTML(ingredient.name)}</span><span class="badge warn">${Number(ingredient.percentage).toFixed(1)}%</span></div>`;
}
/** Open an accessible dialog containing a form. Inputs: title and trusted form markup. Output: none. */
function openDialog(title, content) {
  dialog.innerHTML = `<div class="dialog-heading"><h2 id="dialog-title">${escapeHTML(title)}</h2><button class="close-btn" data-action="close-dialog" aria-label="Close dialog">×</button></div><p class="form-error" id="dialog-error" role="alert"></p>${content}`;
  dialog.showModal();
}
/** Open a create/edit menu dialog. Input: optional product ID. Output: none. */
function editProduct(id) {
  const product = id ? state.adminMenu.products.find(findByID.bind(null, id)) : null;
  openDialog(product ? "Refine a favorite." : "Meet your next favorite.", `<form id="product-form" data-id="${product ? escapeHTML(product.id) : ""}"><label class="field"><span>Drink name</span><input name="name" required maxlength="60" value="${escapeHTML(product?.name || "")}" placeholder="e.g. Matcha Latte"></label><label class="field"><span>Description</span><textarea name="description" maxlength="300" rows="3" required>${escapeHTML(product?.description || "")}</textarea></label><div class="form-grid"><label class="field"><span>Price (USD)</span><input name="price" type="number" min="0.01" max="100" step="0.01" value="${product ? (product.price_cents / 100).toFixed(2) : "4.00"}" required></label><label class="field"><span>Temperature</span><select name="category"><option value="hot" ${product?.category !== "iced" ? "selected" : ""}>Hot</option><option value="iced" ${product?.category === "iced" ? "selected" : ""}>Iced</option></select></label></div><label class="field"><span>Default milk (%)</span><input name="default_milk_percent" type="number" min="0" max="100" step="1" value="${product?.default_milk_percent ?? 40}" required></label>${product ? `<label class="checkbox-field"><input name="active" type="checkbox" ${product.active ? "checked" : ""}> Active on customer menu</label>` : ""}<button class="btn full" type="submit">${product ? "Save changes" : "Add to the collection"} →</button><p class="fine-print">New drinks use a standard coffee base recipe in this prototype.</p></form>`);
}
/** Compare object IDs without relying on numeric vs string transport. Inputs: ID, item. Output: boolean. */
function findByID(id, item) { return String(item.id) === String(id); }
/** Open a simulated stock sensor override dialog. Input: ingredient ID. Output: none. */
function editStock(id) {
  const ingredient = state.inventory.ingredients.find(findByID.bind(null, id));
  if (!ingredient) return;
  openDialog(`Set ${ingredient.name.toLowerCase()} level`, `<form id="stock-form" data-id="${escapeHTML(id)}"><p class="subtext">Simulated sensor override. Capacity: ${escapeHTML(ingredient.capacity)} ${escapeHTML(ingredient.unit)}. Set below ${Number(ingredient.capacity) * .15} to demonstrate the low-level alert.</p><div class="divider"></div><label class="field"><span>Current amount (${escapeHTML(ingredient.unit)})</span><input type="number" name="stock" min="0" max="${Number(ingredient.capacity)}" step="any" value="${Number(ingredient.stock)}" required></label><button type="submit" class="btn full">Save simulated reading →</button></form>`);
}
/** Handle all delegated click controls. Input: click event. Output: Promise<void>. */
async function handleClick(event) {
  const button = event.target.closest("button, a[data-view]");
  if (!button || button.disabled) return;
  try {
    if (button.dataset.view) {
      if (button.dataset.openInventory) state.adminTab = "inventory";
      await navigate(button.dataset.view);
    } else if (button.dataset.category) {
      state.category = button.dataset.category;
      for (const chip of document.querySelectorAll("[data-category]")) chip.classList.toggle("active", chip === button);
      renderProducts();
    } else if (button.dataset.select) {
      if (state.order && state.order.status !== "completed") { notify("Please collect your current drink before starting another."); return; }
      state.order = null; saveOrderID(null);
      selectProduct(button.dataset.select);
    } else if (button.dataset.adminTab) {
      state.adminTab = button.dataset.adminTab; renderAdmin(); applyBarWidths(main);
    } else if (button.dataset.edit) editProduct(button.dataset.edit);
    else if (button.dataset.stock) editStock(button.dataset.stock);
    else await performAction(button.dataset.action);
  } catch (error) { notify(error.message, true); }
}
/** Select a product and initialize its recipe. Input: product ID. Output: none. */
function selectProduct(id) {
  state.selected = id;
  const product = state.menu.products.find(isSelected);
  if (!product) return;
  state.milk = product.default_milk_percent; state.sugar = 0;
  renderOrderPanel();
  document.querySelector("#order-panel").scrollIntoView({behavior: "smooth", block: "nearest"});
}
/** Execute a button action against the API. Input: action identifier. Output: Promise<void>. */
async function performAction(action) {
  if (action === "retry") await initialize();
  else if (action === "clear-selection") { state.selected = null; renderOrderPanel(); }
  else if (action === "close-dialog") dialog.close();
  else if (action === "new-drink") { state.order = null; state.selected = null; saveOrderID(null); renderOrderPanel(); }
  else if (action === "collect") {
    state.order = await api(`/api/orders/${encodeURIComponent(state.order.id)}/collect`, "POST", {});
    state.menu = await api("/api/menu"); render(); notify("Your coffee is ready to enjoy. Have a lovely day!");
  } else if (action === "recommend") {
    state.recommendation = await api("/api/recommendation", "POST", {scenario: state.scenario, hour: state.hour});
    state.weather = state.recommendation.weather;
    if (!state.order || state.order.status === "completed") {
      state.order = null; saveOrderID(null); selectProduct(state.recommendation.product_id);
    }
    renderRecommendation();
    notify(`${state.recommendation.product_name}: ${state.recommendation.reason}`);
  } else if (action === "logout") {
    state.session = await api("/api/auth/logout", "POST", {}); render(); notify("Signed out.");
  } else if (action === "refresh") { await refreshProtected(); render(); notify("Everything is up to date."); }
  else if (action === "add-product") editProduct();
  else if (action === "toggle-service") {
    const result = await api("/api/service/mode", "POST", {enabled: state.session.machine_mode !== "service"});
    state.session.machine_mode = result.machine_mode;
    await refreshProtected(); render(); notify(result.machine_mode === "service" ? "Service mode enabled. Customer ordering is paused." : "Maintenance finished. The machine is ready for customers.");
  }
}
/** Keep interactive filter/recipe controls in state. Input: input/change event. Output: Promise<void>. */
async function handleInput(event) {
  const input = event.target;
  if (input.id === "search") { state.search = input.value; renderProducts(); }
  else if (input.id === "milk" || input.id === "sugar") {
    state[input.id] = Number(input.value);
    document.querySelector(`#${input.id}-value`).textContent = `${input.value}${input.id === "milk" ? "%" : " g"}`;
    document.querySelector("#recipe-preview").textContent = recipeText();
  } else if (input.name === "payment") state.payment = input.value;
  else if (input.id === "payment-result") state.paymentResult = input.value;
  else if ((input.id === "weather-scenario" || input.id === "weather-hour") && event.type === "change") {
    if (input.id === "weather-hour") {
      const value = Number(input.value);
      if (!Number.isInteger(value) || value < 0 || value > 23) { input.value = state.hour; notify("Please choose an hour from 0 to 23.", true); return; }
      state.hour = value;
    } else state.scenario = input.value;
    try {
      state.weather = await api(`/api/weather?scenario=${encodeURIComponent(state.scenario)}&hour=${state.hour}`);
      state.recommendation = null; renderRecommendation();
    } catch (error) { notify(error.message, true); }
  }
}
/** Submit login, checkout, menu editing, inventory, or diagnostics. Input: submit event. Output: Promise<void>. */
async function handleSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const data = new FormData(form);
  const submit = form.querySelector('button[type="submit"]');
  if (submit?.disabled) return;
  if (submit) submit.disabled = true;
  try {
    if (form.id === "login-form") {
      state.session = await api("/api/auth/login", "POST", {role: form.dataset.role, credential: data.get("credential")});
      await refreshProtected(); render(); notify("Welcome to your workspace.");
    } else if (form.id === "checkout-form") {
      state.busy = true;
      state.order = await api("/api/orders", "POST", {product_id: state.selected, milk_percent: state.milk, sugar_grams: state.sugar, payment_method: state.payment, payment_result: state.paymentResult});
      saveOrderID(state.order.id); state.menu = await api("/api/menu");
      renderProducts(); renderOrderPanel(); notify("Payment approved. Your coffee is brewing!");
    } else if (form.id === "product-form") {
      const body = {name: data.get("name"), description: data.get("description"), category: data.get("category"), price_cents: Math.round(Number(data.get("price")) * 100), default_milk_percent: Number(data.get("default_milk_percent"))};
      if (form.dataset.id) body.active = data.has("active");
      await api(`/api/admin/menu${form.dataset.id ? `/${encodeURIComponent(form.dataset.id)}` : ""}`, form.dataset.id ? "PATCH" : "POST", body);
      await refreshProtected(); dialog.close(); render(); notify("The coffee collection has been updated.");
    } else if (form.id === "stock-form") {
      state.inventory = await api(`/api/inventory/${encodeURIComponent(form.dataset.id)}`, "POST", {stock: Number(data.get("stock"))});
      dialog.close(); renderAdmin(); applyBarWidths(main); notify("Simulated sensor reading saved.");
    } else if (form.classList.contains("diagnostic-form")) {
      state.busy = true; renderService();
      state.diagnostics[form.dataset.component] = await api("/api/service/diagnostics", "POST", {component: form.dataset.component, simulate_fault: data.has("simulate_fault")});
      await refreshProtected();
      notify(state.diagnostics[form.dataset.component].passed ? "Simulated diagnostic completed successfully." : "Simulated fault detected and recorded in the event log.", !state.diagnostics[form.dataset.component].passed);
    }
  } catch (error) {
    if (dialog.open) document.querySelector("#dialog-error").textContent = error.message;
    else notify(error.message, true);
  } finally {
    state.busy = false;
    if (submit?.isConnected) submit.disabled = false;
    if (form.classList.contains("diagnostic-form")) renderService();
  }
}
/** Poll only an active brewing order, updating progress without resetting forms. Input: none. Output: Promise<void>. */
async function pollOrder() {
  if (polling || !state.order || state.order.status !== "brewing") return;
  polling = true;
  try {
    const order = await api(`/api/orders/${encodeURIComponent(state.order.id)}`);
    const becameReady = order.status === "ready";
    state.order = order;
    if (state.view === "brew") renderOrderPanel();
    if (becameReady) notify("Your coffee is ready. Time for a little pause!");
  } catch (error) { /* A transient connection failure keeps the last known order visible; the next interval retries. */ }
  finally { polling = false; }
}

document.addEventListener("click", handleClick);
document.addEventListener("input", handleInput);
document.addEventListener("change", handleInput);
document.addEventListener("submit", handleSubmit);
setInterval(pollOrder, 1000);
initialize();
