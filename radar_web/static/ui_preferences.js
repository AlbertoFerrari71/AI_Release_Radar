(function () {
  function withLanguage(url, language) {
    const target = new URL(url, window.location.origin);
    target.searchParams.set("lang", language);
    return target.toString();
  }

  async function savePreferences(payload) {
    const response = await fetch("/api/preferences/ui", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `HTTP ${response.status}`);
    }
    return response.json();
  }

  function bindLanguageSelect() {
    const select = document.querySelector("[data-ui-language-select]");
    if (!select) {
      return;
    }
    select.addEventListener("change", async () => {
      const language = select.value;
      try {
        await savePreferences({
          language,
          last_selected_language: language
        });
      } finally {
        window.location.assign(withLanguage(window.location.href, language));
      }
    });
  }

  function bindStartModeSelect() {
    const select = document.querySelector("[data-ui-start-mode-select]");
    if (!select) {
      return;
    }
    select.addEventListener("change", async () => {
      const mode = select.value;
      await savePreferences({
        start_mode: mode,
        last_selected_mode: mode
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindLanguageSelect();
    bindStartModeSelect();
  });
})();
