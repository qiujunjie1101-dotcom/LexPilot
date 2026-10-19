import { ref } from 'vue';

export type Theme = 'light' | 'dark';

const theme = ref<Theme>('light');
let initialized = false;

function applyTheme(next: Theme, persist = true) {
  theme.value = next;
  document.documentElement.classList.toggle('dark', next === 'dark');
  if (persist) localStorage.setItem('legal-theme', next);
}

export function initTheme() {
  if (initialized || typeof window === 'undefined') return;
  initialized = true;
  const stored = localStorage.getItem('legal-theme');
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  applyTheme(stored === 'dark' || stored === 'light' ? stored : prefersDark ? 'dark' : 'light', false);
}

export function useTheme() {
  initTheme();

  const toggleTheme = () => {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark');
  };

  const setTheme = (next: Theme) => {
    applyTheme(next);
  };

  return { theme, toggleTheme, setTheme };
}
