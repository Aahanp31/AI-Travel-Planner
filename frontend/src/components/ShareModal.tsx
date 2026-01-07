'use client';

import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import {
  XMarkIcon,
  LinkIcon,
  CheckIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  shareToken: string;
  tripName: string;
}

export default function ShareModal({ isOpen, onClose, shareToken, tripName }: ShareModalProps) {
  const [copied, setCopied] = useState(false);

  // Use window.location.origin to work in both dev and production
  const shareUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/shared/${shareToken}`
    : '';

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const shareViaWhatsApp = () => {
    const text = encodeURIComponent(`Check out my trip: ${tripName}\n${shareUrl}`);
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  const shareViaEmail = () => {
    const subject = encodeURIComponent(`Check out my trip: ${tripName}`);
    const body = encodeURIComponent(`I planned an amazing trip and wanted to share it with you!\n\nTrip: ${tripName}\n\nView the full itinerary here: ${shareUrl}`);
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl glass-card border border-border-subtle p-6 shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <Dialog.Title className="text-2xl font-bold text-foreground">
                    Share Trip
                  </Dialog.Title>
                  <button
                    onClick={onClose}
                    className="p-2 rounded-lg hover:bg-muted transition-colors"
                  >
                    <XMarkIcon className="w-5 h-5 text-muted-foreground" />
                  </button>
                </div>

                {/* Trip Name */}
                <div className="mb-6">
                  <p className="text-sm text-muted-foreground mb-1">Sharing</p>
                  <p className="text-lg font-semibold text-foreground">{tripName}</p>
                </div>

                {/* Share URL */}
                <div className="mb-6">
                  <label className="text-sm font-medium text-muted-foreground mb-2 block">
                    Share Link
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={shareUrl}
                      readOnly
                      className="flex-1 px-4 py-3 bg-muted/50 border border-border-subtle rounded-xl text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                    <button
                      onClick={handleCopyLink}
                      className={`px-4 py-3 rounded-xl font-medium transition-all ${
                        copied
                          ? 'bg-green-500 text-white'
                          : 'bg-gradient-to-br from-primary to-accent text-primary-foreground hover:shadow-lg'
                      }`}
                    >
                      {copied ? (
                        <CheckIcon className="w-5 h-5" />
                      ) : (
                        <LinkIcon className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  {copied && (
                    <p className="text-xs text-green-500 mt-2">Link copied to clipboard!</p>
                  )}
                </div>

                {/* Social Share Buttons */}
                <div className="space-y-3">
                  <p className="text-sm font-medium text-muted-foreground">Share via</p>

                  {/* WhatsApp */}
                  <button
                    onClick={shareViaWhatsApp}
                    className="w-full flex items-center gap-3 px-4 py-3 bg-[#25D366] hover:bg-[#20BA5A] text-white rounded-xl transition-colors"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                    </svg>
                    <span className="font-semibold">WhatsApp</span>
                  </button>

                  {/* Email */}
                  <button
                    onClick={shareViaEmail}
                    className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors"
                  >
                    <EnvelopeIcon className="w-5 h-5" />
                    <span className="font-semibold">Email</span>
                  </button>
                </div>

                {/* Info */}
                <div className="mt-6 p-3 bg-muted/30 rounded-xl">
                  <p className="text-xs text-muted-foreground">
                    Anyone with this link can view your trip itinerary, but they cannot edit it.
                  </p>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
