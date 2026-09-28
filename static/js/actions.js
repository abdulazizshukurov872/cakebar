/* Progressive enhancement for favorite / cart forms: intercepts the submit,
 * does the same POST in the background, and updates just the affected bit
 * of the page instead of a full navigation — no reload, no scroll jump.
 * Every form still has a normal action/method, so with JS disabled (or on
 * any error) it falls back to a real submit and works exactly as before. */
(function () {
  function csrfToken(form) {
    var el = form.querySelector("[name=csrfmiddlewaretoken]");
    return el ? el.value : "";
  }

  function updateCartBadge(count) {
    var el = document.getElementById("cart-count-badge");
    if (el) el.textContent = "(" + count + ")";
  }

  function showToast(text, icon) {
    var stack = document.getElementById("toast-stack");
    if (!stack || !text) return;
    var toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = '<span class="toast-icon">' + (icon || "✓") + "</span><span>" + text + "</span>";
    stack.appendChild(toast);
    requestAnimationFrame(function () { toast.classList.add("show"); });
    setTimeout(function () {
      toast.classList.remove("show");
      setTimeout(function () { toast.remove(); }, 250);
    }, 2200);
  }

  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    var action = form.getAttribute("action") || "";

    // --- Favorite toggle ---
    if (/\/favorites\/toggle\/\d+\/?$/.test(action)) {
      e.preventDefault();
      var favBtn = form.querySelector("button[type=submit]");
      fetch(action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: new FormData(form),
        credentials: "same-origin",
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.auth_required) { window.location.href = data.login_url; return; }
          if (!data.ok || !favBtn) return;
          var isFav = data.is_favorite;
          favBtn.classList.toggle("active", isFav);
          if (favBtn.classList.contains("fav-btn")) {
            favBtn.textContent = isFav ? "♥" : "♡";
          } else {
            favBtn.innerHTML = isFav
              ? "♥ " + (favBtn.dataset.inFavorites || "Sevimlilarda")
              : "♡ " + (favBtn.dataset.addFavorites || "Sevimlilarga qo'shish");
          }
          var body = document.body;
          showToast(isFav ? body.dataset.toastAddedFav : body.dataset.toastRemovedFav, isFav ? "♥" : "♡");
        })
        .catch(function () { form.submit(); });
      return;
    }

    // --- Add to cart ---
    if (/\/cart\/add\/\d+\/?$/.test(action)) {
      e.preventDefault();
      var addBtn = form.querySelector("button[type=submit]");
      var original = addBtn ? addBtn.textContent : "";
      fetch(action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: new FormData(form),
        credentials: "same-origin",
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!data.ok) return;
          updateCartBadge(data.cart_count);
          if (addBtn) {
            addBtn.textContent = "✓";
            setTimeout(function () { addBtn.textContent = original; }, 900);
          }
          showToast(document.body.dataset.toastAddedCart, "🛒");
        })
        .catch(function () { form.submit(); });
      return;
    }

    // --- Cart page: qty +/- and remove (re-renders just the cart card) ---
    if (/\/cart\/update\/|\/cart\/remove\//.test(action)) {
      e.preventDefault();
      var fd = new FormData(form);
      if (e.submitter && e.submitter.name) fd.set(e.submitter.name, e.submitter.value);
      fetch(action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: fd,
        credentials: "same-origin",
      })
        .then(function (r) {
          var count = r.headers.get("X-Cart-Count");
          if (count !== null) updateCartBadge(count);
          return r.text();
        })
        .then(function (html) {
          var body = document.getElementById("cart-body");
          if (body) {
            var wrapper = document.createElement("div");
            wrapper.innerHTML = html;
            var fresh = wrapper.querySelector("#cart-body");
            if (fresh) body.replaceWith(fresh);
          }
        })
        .catch(function () { form.submit(); });
      return;
    }
  });
})();
