
const I18N = (() => {
  const dict = {
    uk: {
      appTag: "CryptoTaro • AI-помічник",
      navDashboard: "Дашборд",
      navMarket: "Ринок",
      navAI: "AI-аналіз",
      navAI: "AI-аналітика",
      navCalculator: "Калькулятор",
      navPortfolio: "Портфель",
      navSettings: "Налаштування",
      navProfile: "Профіль",
      logout: "Вийти",
      connect: "Підключення",
      online: "Онлайн",
      offline: "Офлайн",
      provider: "Провайдер",
      gemini: "Gemini",
      openai: "OpenAI",
      language: "Мова",
      symbol: "Символ",
      load: "Завантажити",
      pin: "Закріпити",
      refresh: "Оновити",
      lastPrice: "Остання ціна",
      change24h: "Зміна 24г",
      volume24h: "Обсяг 24г",
      marketCap: "Капіталізація",
      dominance: "Домінування",
      chart: "Графік",
      candles: "Свічки",
      line: "Лінія",
      historyLimit: "Історія (точок)",
      aiShort: "Короткий розбір",
      runAnalysis: "Зробити аналіз",
      analysisResult: "Результат",
      portfolioTotal: "Загальна вартість",
      portfolioAnalysis: "AI-огляд портфеля",
      holdings: "Позиції",
      add: "Додати",
      remove: "Зняти",
      assetId: "ID активу",
      amount: "Кількість",
      save: "Зберегти",
      profile: "Профіль",
      updateProfile: "Оновити профіль",
      unlinkDiscord: "Відвʼязати Discord",
      twofa: "2FA",
      tipPin: "Підказка: закріплену монету можна зберігати в профілі та показувати на дашборді.",
      needAuth: "Потрібна авторизація. Повертаю на сторінку входу.",
      apiError: "Помилка API",
      ok: "Гаразд",
      cancel: "Скасувати",
      wsLive: "Live (Binance WS)",
      wsNotAvailable: "WS недоступний — використовуємо бекенд",
      noteCORS: "",
      calcTitle: "Калькулятор",
      calcSubtitle: "Швидкий розрахунок вартості",
      runCalc: "Розрахувати",
      calcResult: "Результат",
      calcPrice: "Ціна",
      calcTotal: "Вартість",
      calcUpdated: "Оновлено",
      calcHint: "Ціна з останнього запису або свіжого запиту.",
      calcEmpty: "Введіть символ і кількість, щоб порахувати."
    },
    en: {
      appTag: "CryptoTaro • AI assistant",
      navDashboard: "Dashboard",
      navMarket: "Market",
      navAI: "AI Analysis",
      navCalculator: "Calculator",
      navPortfolio: "Portfolio",
      navSettings: "Settings",
      navProfile: "Profile",
      logout: "Logout",
      connect: "Connection",
      online: "Online",
      offline: "Offline",
      provider: "Provider",
      gemini: "Gemini",
      openai: "OpenAI",
      language: "Language",
      symbol: "Symbol",
      load: "Load",
      pin: "Pin",
      refresh: "Refresh",
      lastPrice: "Last price",
      change24h: "24h change",
      volume24h: "24h volume",
      marketCap: "Market cap",
      dominance: "Dominance",
      chart: "Chart",
      candles: "Candles",
      line: "Line",
      historyLimit: "History (points)",
      aiShort: "Short analysis",
      runAnalysis: "Run analysis",
      analysisResult: "Result",
      portfolioTotal: "Total value",
      portfolioAnalysis: "AI portfolio review",
      holdings: "Holdings",
      add: "Add",
      remove: "Remove",
      assetId: "Asset ID",
      amount: "Amount",
      save: "Save",
      profile: "Profile",
      updateProfile: "Update profile",
      unlinkDiscord: "Unlink Discord",
      twofa: "2FA",
      tipPin: "Tip: pinned coin can be saved in profile and shown on dashboard.",
      needAuth: "Authentication required. Redirecting to login.",
      apiError: "API error",
      ok: "OK",
      cancel: "Cancel",
      wsLive: "Live (Binance WS)",
      wsNotAvailable: "WS unavailable — using backend",
      noteCORS: "",
      calcTitle: "Calculator",
      calcSubtitle: "Quick value calculator",
      runCalc: "Calculate",
      calcResult: "Result",
      calcPrice: "Price",
      calcTotal: "Total",
      calcUpdated: "Updated",
      calcHint: "Price uses last DB record or fresh fetch.",
      calcEmpty: "Enter symbol and amount to calculate."
    }
  };

  const getLang = () => localStorage.getItem("ct_lang") || "uk";
  const setLang = (lang) => localStorage.setItem("ct_lang", lang);

  const t = (key) => {
    const lang = getLang();
    return (dict[lang] && dict[lang][key]) || (dict.en[key] || key);
  };

  const apply = () => {
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      el.textContent = t(key);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.getAttribute("data-i18n-placeholder");
      el.setAttribute("placeholder", t(key));
    });
  };

  return { t, getLang, setLang, apply };
})();
