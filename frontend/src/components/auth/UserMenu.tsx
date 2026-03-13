'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import AuthModal from './AuthModal';
import {
  UserCircleIcon,
  BookmarkIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  UserIcon
} from '@heroicons/react/24/outline';

export default function UserMenu() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [showDropdown, setShowDropdown] = useState(false);

  if (!user) {
    return (
      <>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setAuthMode('signin');
              setShowAuthModal(true);
            }}
            className="px-4 py-2 text-sm font-medium text-foreground hover:text-primary transition-colors rounded-lg hover:bg-muted"
          >
            Sign In
          </button>
          <button
            onClick={() => {
              setAuthMode('signup');
              setShowAuthModal(true);
            }}
            className="px-4 py-2 text-sm font-medium bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-lg hover:shadow-lg transition-all"
          >
            Sign Up
          </button>
        </div>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          defaultMode={authMode}
        />
      </>
    );
  }

  return (
    <div className="relative">
      {/* User Avatar Button */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-muted transition-colors"
      >
        {user.profile_picture ? (
          <img
            src={user.profile_picture}
            alt={user.username}
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground font-semibold text-sm">
            {user.username.charAt(0).toUpperCase()}
          </div>
        )}
        <span className="text-sm font-medium text-foreground hidden sm:inline">
          {user.username}
        </span>
      </button>

      {/* Dropdown Menu */}
      {showDropdown && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowDropdown(false)}
          ></div>

          {/* Menu */}
          <div className="absolute top-12 right-0 z-50 w-56 bg-background border border-border-subtle rounded-xl shadow-2xl overflow-hidden animate-fadeIn">
            {/* User info */}
            <div className="px-4 py-3 border-b border-border-subtle">
              <p className="text-sm font-semibold text-foreground">{user.username}</p>
              <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            </div>

            {/* Menu items */}
            <div className="py-2">
              <button
                onClick={() => {
                  router.push('/profile');
                  setShowDropdown(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-foreground hover:bg-muted transition-colors"
              >
                <Cog6ToothIcon className="w-5 h-5 text-muted-foreground" />
                Profile Settings
              </button>

              <button
                onClick={() => {
                  router.push('/saved-trips');
                  setShowDropdown(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-foreground hover:bg-muted transition-colors"
              >
                <BookmarkIcon className="w-5 h-5 text-muted-foreground" />
                Saved Trips ({user.trip_count})
              </button>
            </div>

            {/* Sign out */}
            <div className="border-t border-border-subtle py-2">
              <button
                onClick={() => {
                  logout();
                  setShowDropdown(false);
                  router.push('/');
                }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-destructive hover:bg-destructive/10 transition-colors"
              >
                <ArrowRightOnRectangleIcon className="w-5 h-5" />
                Sign Out
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
