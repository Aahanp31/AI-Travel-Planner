'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800">
        <div className="w-6 h-6" />
      </button>
    );
  }

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-3 rounded-xl glass-card hover:scale-105 transition-all duration-300 group border border-border-subtle"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <SunIcon className="w-6 h-6 text-warning group-hover:rotate-90 transition-transform duration-500" />
      ) : (
        <MoonIcon className="w-6 h-6 text-primary group-hover:-rotate-12 transition-transform duration-500" />
      )}
    </button>
  );
}
