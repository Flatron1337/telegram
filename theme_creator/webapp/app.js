/**
 * Telegram Theme Studio - WebApp Client Logic
 */

// Initialize Telegram WebApp SDK safely
const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;

if (tg) {
  try {
    tg.ready();
    tg.expand();
  } catch (err) {
    console.warn("Telegram WebApp initialization error:", err);
  }
}

// Preset definitions
const PRESETS = {
  rem: {
    name: "Cyberpunk Rem Glass",
    accent: "#00E5FF",
    bg: "#0B0E14",
    inBubble: "#16202C",
    outBubble: "#005577",
    isDark: true,
  },
  ram: {
    name: "Cyberpunk Ram Glass",
    accent: "#FF3C8A",
    bg: "#140A17",
    inBubble: "#29152E",
    outBubble: "#7A1244",
    isDark: true,
  },
  amoled: {
    name: "AMOLED Pure Neon",
    accent: "#00FF88",
    bg: "#000000",
    inBubble: "#121212",
    outBubble: "#004726",
    isDark: true,
  },
  sunset: {
    name: "Sunset Purple Glass",
    accent: "#FF8800",
    bg: "#160C24",
    inBubble: "#28173E",
    outBubble: "#6E2400",
    isDark: true,
  },
  emerald: {
    name: "Emerald Mint Glass",
    accent: "#22E690",
    bg: "#0C1712",
    inBubble: "#142820",
    outBubble: "#0A5433",
    isDark: true,
  },
};

// State
let isDarkTheme = true;
let hasTransparency = true;
let inOpacity = 0.75;
let outOpacity = 0.85;
let blurRadius = 12;

// DOM Elements
const elements = {
  modeToggle: document.getElementById("modeToggle"),
  themeName: document.getElementById("themeName"),
  accentColor: document.getElementById("accentColor"),
  accentText: document.getElementById("accentText"),
  bgColor: document.getElementById("bgColor"),
  bgText: document.getElementById("bgText"),
  inBubbleColor: document.getElementById("inBubbleColor"),
  inBubbleText: document.getElementById("inBubbleText"),
  outBubbleColor: document.getElementById("outBubbleColor"),
  outBubbleText: document.getElementById("outBubbleText"),

  transparencyToggle: document.getElementById("transparencyToggle"),
  transparencySliders: document.getElementById("transparencySliders"),
  inAlphaSlider: document.getElementById("inAlphaSlider"),
  inAlphaVal: document.getElementById("inAlphaVal"),
  outAlphaSlider: document.getElementById("outAlphaSlider"),
  outAlphaVal: document.getElementById("outAlphaVal"),
  blurSlider: document.getElementById("blurSlider"),
  blurVal: document.getElementById("blurVal"),

  mockupTopBar: document.getElementById("mockupTopBar"),
  mockupChatBody: document.getElementById("mockupChatBody"),
  mockupAvatar: document.getElementById("mockupAvatar"),
  mockupAuthor: document.getElementById("mockupAuthor"),
  mockupInBubble: document.getElementById("mockupInBubble"),
  mockupOutBubble: document.getElementById("mockupOutBubble"),
  mockupInputBar: document.getElementById("mockupInputBar"),

  applyBtn: document.getElementById("applyBtn"),
  toast: document.getElementById("toast"),
  presetChips: document.querySelectorAll(".preset-chip"),
};

// Convert hex to rgb
function hexToRgb(hex) {
  let clean = hex.replace("#", "").trim();
  if (clean.length === 3) {
    clean = clean.split("").map((c) => c + c).join("");
  }
  const num = parseInt(clean, 16);
  return {
    r: (num >> 16) & 255,
    g: (num >> 8) & 255,
    b: num & 255,
  };
}

// Convert rgb + alpha to rgba string
function toRgba(hex, alpha) {
  const rgb = hexToRgb(hex);
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
}

// Sync hex text and color picker
function linkColorInputs(picker, textInput) {
  picker.addEventListener("input", (e) => {
    textInput.value = e.target.value.toUpperCase();
    updateLivePreview();
  });
  textInput.addEventListener("input", (e) => {
    let val = e.target.value.trim();
    if (!val.startsWith("#")) val = "#" + val;
    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
      picker.value = val;
      updateLivePreview();
    }
  });
}

linkColorInputs(elements.accentColor, elements.accentText);
linkColorInputs(elements.bgColor, elements.bgText);
linkColorInputs(elements.inBubbleColor, elements.inBubbleText);
linkColorInputs(elements.outBubbleColor, elements.outBubbleText);

// Transparency Sliders
elements.transparencyToggle.addEventListener("change", (e) => {
  hasTransparency = e.target.checked;
  if (hasTransparency) {
    elements.transparencySliders.classList.remove("disabled");
  } else {
    elements.transparencySliders.classList.add("disabled");
  }
  updateLivePreview();
});

elements.inAlphaSlider.addEventListener("input", (e) => {
  inOpacity = parseInt(e.target.value, 10) / 100;
  elements.inAlphaVal.textContent = `${e.target.value}%`;
  updateLivePreview();
});

elements.outAlphaSlider.addEventListener("input", (e) => {
  outOpacity = parseInt(e.target.value, 10) / 100;
  elements.outAlphaVal.textContent = `${e.target.value}%`;
  updateLivePreview();
});

elements.blurSlider.addEventListener("input", (e) => {
  blurRadius = parseInt(e.target.value, 10);
  elements.blurVal.textContent = `${blurRadius}px`;
  updateLivePreview();
});

// Update Live Preview Mockup
function updateLivePreview() {
  const accent = elements.accentColor.value;
  const bg = elements.bgColor.value;
  const inColor = elements.inBubbleColor.value;
  const outColor = elements.outBubbleColor.value;

  // Background
  elements.mockupChatBody.style.backgroundColor = bg;

  // Header and Avatar
  elements.mockupAvatar.style.backgroundColor = accent;
  elements.mockupAuthor.style.color = accent;

  // Bubbles
  const currentInAlpha = hasTransparency ? inOpacity : 1.0;
  const currentOutAlpha = hasTransparency ? outOpacity : 1.0;
  const currentBlur = hasTransparency ? `${blurRadius}px` : "0px";

  elements.mockupInBubble.style.backgroundColor = toRgba(inColor, currentInAlpha);
  elements.mockupInBubble.style.backdropFilter = `blur(${currentBlur})`;
  elements.mockupInBubble.style.webkitBackdropFilter = `blur(${currentBlur})`;

  elements.mockupOutBubble.style.backgroundColor = toRgba(outColor, currentOutAlpha);
  elements.mockupOutBubble.style.backdropFilter = `blur(${currentBlur})`;
  elements.mockupOutBubble.style.webkitBackdropFilter = `blur(${currentBlur})`;

  // CSS variable accent update
  document.documentElement.style.setProperty("--accent", accent);
}

// Preset selection
elements.presetChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    elements.presetChips.forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");

    const presetKey = chip.dataset.preset;
    const p = PRESETS[presetKey];
    if (!p) return;

    elements.themeName.value = p.name;
    elements.accentColor.value = p.accent;
    elements.accentText.value = p.accent;
    elements.bgColor.value = p.bg;
    elements.bgText.value = p.bg;
    elements.inBubbleColor.value = p.inBubble;
    elements.inBubbleText.value = p.inBubble;
    elements.outBubbleColor.value = p.outBubble;
    elements.outBubbleText.value = p.outBubble;

    updateLivePreview();
  });
});

// Dark / Light toggle
elements.modeToggle.addEventListener("click", () => {
  isDarkTheme = !isDarkTheme;
  document.body.setAttribute("data-theme", isDarkTheme ? "dark" : "light");
  elements.modeToggle.querySelector(".mode-icon").textContent = isDarkTheme ? "🌙" : "☀️";
  updateLivePreview();
});

// Toast notification
function showToast(text) {
  elements.toast.textContent = text;
  elements.toast.classList.add("show");
  setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2800);
}

// Apply Theme
elements.applyBtn.addEventListener("click", async () => {
  const payload = {
    name: elements.themeName.value.trim() || "Custom Theme",
    is_dark: isDarkTheme,
    accent: elements.accentColor.value,
    background: elements.bgColor.value,
    in_bubble: elements.inBubbleColor.value,
    out_bubble: elements.outBubbleColor.value,
    in_bubble_alpha: hasTransparency ? Math.round(inOpacity * 255) : 255,
    out_bubble_alpha: hasTransparency ? Math.round(outOpacity * 255) : 255,
    has_transparency: hasTransparency,
  };

  const originalText = elements.applyBtn.textContent;
  elements.applyBtn.disabled = true;
  elements.applyBtn.textContent = "⏳ Отправка темы в чат...";

  const userId = tg && tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : null;
  const initData = tg ? tg.initData : "";

  // 1. Send via Backend API (works for Inline buttons, Menu button, and direct links)
  try {
    const res = await fetch("/api/apply-theme", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        init_data: initData,
        theme: payload,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.status === "ok") {
        showToast("✨ Тема готова и отправлена вам в чат!");
        setTimeout(() => {
          if (tg && typeof tg.close === "function") {
            tg.close();
          }
        }, 1200);
        return;
      }
    }
  } catch (err) {
    console.warn("Backend apply-theme API error:", err);
  }

  // 2. Fallback to tg.sendData if opened via Reply Keyboard
  if (tg && typeof tg.sendData === "function") {
    try {
      tg.sendData(JSON.stringify(payload));
      showToast("✨ Тема отправлена боту!");
      setTimeout(() => {
        tg.close();
      }, 500);
      return;
    } catch (e) {
      console.warn("tg.sendData fallback error:", e);
    }
  }

  elements.applyBtn.disabled = false;
  elements.applyBtn.textContent = originalText;
  showToast("✨ Тема настроена! Вернитесь в чат с ботом.");
});

// Initialize on page load
updateLivePreview();
