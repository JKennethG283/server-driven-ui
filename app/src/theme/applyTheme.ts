import type { Theme } from "./themeMap";

// Writes a Theme onto the CSS custom-property slots that index.css already uses,
// reskinning the whole app. Also exposes the motion kind + backdrop image.
export function applyTheme(theme: Theme, el: HTMLElement = document.documentElement) {
  const set = (name: string, value: string) => el.style.setProperty(name, value);

  set("--night", theme.night);
  set("--night-2", theme.night2);
  set("--night-3", theme.night3);
  set("--raise", theme.raise);
  set("--raise-2", theme.raise2);

  set("--gold", theme.accent);
  set("--amber", theme.accent2);
  set("--sky", theme.sky);
  set("--violet", theme.violet);
  set("--violet-soft", theme.violetSoft);
  set("--cream", theme.cream);

  set("--text", theme.text);
  set("--text-dim", theme.textDim);
  set("--text-faint", theme.textFaint);

  set("--line", theme.line);
  set("--line-strong", theme.lineStrong);
  set("--glow-gold", theme.glow);

  set("--font-display", theme.fontDisplay);
  set("--font-body", theme.fontBody);
  set("--font-mono", theme.fontMono);

  el.dataset.motion = theme.motion;
  if (theme.backdrop) {
    set("--backdrop", `url("${theme.backdrop}")`);
    el.dataset.backdrop = "on";
  } else {
    set("--backdrop", "none");
    el.dataset.backdrop = "off";
  }
}
