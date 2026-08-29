import { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';

function getInitialTheme() {
  // index.html already set this on <html> before React mounted (avoids a
  // flash of the wrong theme), so just read it back.
  const attr = document.documentElement.getAttribute('data-theme');
  return attr === 'light' ? 'light' : 'dark';
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('theme', theme);
    } catch {
      // localStorage can throw in private-browsing / restricted contexts —
      // the toggle still works for the current session either way.
    }
  }, [theme]);

  const isLight = theme === 'light';

  return (
    <button
      type="button"
      className="theme-toggle"
      data-active={isLight}
      onClick={() => setTheme(isLight ? 'dark' : 'light')}
      aria-label={`Switch to ${isLight ? 'dark' : 'light'} mode`}
      aria-pressed={isLight}
    >
      <span className="theme-toggle-label">
        {isLight ? <Sun size={16} /> : <Moon size={16} />}
        {isLight ? 'Light mode' : 'Dark mode'}
      </span>
      <span className="theme-toggle-track">
        <span className="theme-toggle-thumb" />
      </span>
    </button>
  );
}
