/* Product archive: lightweight, accessible search + group filters. */
(function () {
  const search = document.getElementById("product-search");
  const cards = Array.from(document.querySelectorAll("[data-product-card]"));
  const buttons = Array.from(document.querySelectorAll("[data-product-group]"));
  const count = document.getElementById("product-result-count");
  const empty = document.getElementById("product-no-results");
  if (!search || !cards.length) return;

  let selectedGroup = "all";
  function refresh() {
    const query = search.value.trim().toLocaleLowerCase("ja-JP").replace(/\s+/g, "");
    let visible = 0;
    cards.forEach(function (card) {
      const content = (card.dataset.search || "").toLocaleLowerCase("ja-JP").replace(/\s+/g, "");
      const groupMatch = selectedGroup === "all" || card.dataset.group === selectedGroup;
      const matches = content.includes(query) && groupMatch;
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    buttons.forEach(function (button) {
      const active = button.dataset.productGroup === selectedGroup;
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    if (count) count.textContent = visible + "件の商品";
    if (empty) empty.hidden = visible !== 0;
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      selectedGroup = button.dataset.productGroup || "all";
      refresh();
    });
  });
  search.addEventListener("input", refresh);
  refresh();
}());
