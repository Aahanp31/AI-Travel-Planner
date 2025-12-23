'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import dynamic from 'next/dynamic';
import axios from 'axios';
import ItineraryCard from '@/components/ItineraryCard';
import BudgetCard from '@/components/BudgetCard';
import BookingsCard from '@/components/BookingsCard';
import WeatherCard from '@/components/WeatherCard';
import NewsCard from '@/components/NewsCard';
import ChatBot from '@/components/ChatBot';
import AuthModal from '@/components/AuthModal';
import { TripResponse } from '@/types';
import {
  ArrowLeftIcon,
  MapPinIcon,
  ClockIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  MapIcon,
  CloudIcon,
  NewspaperIcon,
  BookmarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

// Import MapEmbed dynamically to avoid SSR issues with Leaflet
const MapEmbed = dynamic(() => import('@/components/MapEmbed'), {
  ssr: false,
  loading: () => <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-md h-[600px] flex items-center justify-center text-gray-500">Loading map...</div>
});

type TabType = 'itinerary' | 'budget' | 'bookings' | 'map' | 'weather' | 'news';

export default function TripPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [tripData, setTripData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<TabType>('itinerary');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [tripName, setTripName] = useState('');
  const [notes, setNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const data = sessionStorage.getItem('tripData');
    if (data) {
      const parsed = JSON.parse(data);
      setTripData(parsed);
      // Set default trip name
      const defaultName = parsed.locations && parsed.locations !== 'AI Selected'
        ? `Trip to ${parsed.locations}`
        : `Trip to ${parsed.country}`;
      setTripName(defaultName);
    }
  }, []);

  const handleSaveTrip = async () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    if (!tripName.trim()) {
      alert('Please enter a trip name');
      return;
    }

    setIsSaving(true);

    try {
      await axios.post(
        'http://localhost:4000/api/auth/save-trip',
        {
          trip_name: tripName,
          country: tripData.country,
          locations: tripData.locations,
          days: tripData.days,
          origin: tripData.origin,
          start_date: tripData.startDate,
          trip_pace: tripData.tripPace,
          itinerary: tripData.result.itinerary,
          budget: tripData.result.budget,
          bookings: tripData.result.bookings,
          mapData: tripData.result.mapData,
          weather: tripData.result.weather,
          news: tripData.result.news,
          notes: notes
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          }
        }
      );

      setSaved(true);
      setShowSaveModal(false);
      setTimeout(() => setSaved(false), 3000);
    } catch (error: any) {
      console.error('Save trip error:', error);
      alert(error.response?.data?.error || 'Failed to save trip');
    } finally {
      setIsSaving(false);
    }
  };

  if (!tripData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="glass-card p-10 rounded-2xl shadow-2xl border border-border-subtle max-w-md w-full text-center">
          <div className="w-16 h-16 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
            <MapPinIcon className="w-8 h-8 text-muted-foreground" />
          </div>
          <h2 className="text-card-foreground mb-3 text-2xl font-bold">
            No trip data found
          </h2>
          <p className="text-muted-foreground mb-6">
            Please plan a trip first to view your itinerary
          </p>
          <button
            onClick={() => router.push('/')}
            className="bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold py-3 px-6 rounded-xl transition-all hover:shadow-lg hover:scale-105"
          >
            Plan a Trip
          </button>
        </div>
      </div>
    );
  }

  const { result, country, locations, days, origin, startDate } = tripData;
  const { itinerary, budget, bookings, mapData, weather, news }: TripResponse = result;

  // Display title - locations if specified, otherwise country
  const displayTitle = locations && locations !== 'AI Selected' ? locations : country;
  const displaySubtitle = locations && locations !== 'AI Selected' ? `Exploring ${country}` : null;

  // Calculate end date
  const endDate = startDate ? new Date(new Date(startDate).getTime() + (days - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : '';

  const tabs = [
    { id: 'itinerary' as TabType, label: 'Itinerary', icon: CalendarDaysIcon },
    { id: 'budget' as TabType, label: 'Budget', icon: CurrencyDollarIcon },
    { id: 'bookings' as TabType, label: 'Bookings', icon: BuildingOfficeIcon },
    { id: 'map' as TabType, label: 'Map', icon: MapIcon },
    { id: 'weather' as TabType, label: 'Weather', icon: CloudIcon },
    { id: 'news' as TabType, label: 'News', icon: NewspaperIcon },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Fixed Header */}
      <div className="sticky top-0 z-50 bg-background/95 backdrop-blur-lg border-b border-border-subtle">
        <div className="max-w-[1400px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4 pr-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                <MapPinIcon className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl md:text-2xl font-bold text-foreground">
                  {displayTitle}
                </h1>
                {displaySubtitle && (
                  <p className="text-xs text-muted-foreground">{displaySubtitle}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {saved && (
                <div className="flex items-center gap-2 px-4 py-2 bg-success/10 border border-success/20 rounded-lg text-success text-sm font-medium">
                  <CheckCircleIcon className="w-4 h-4" />
                  <span className="hidden sm:inline">Saved!</span>
                </div>
              )}
              <button
                onClick={() => setShowSaveModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-lg text-sm font-medium hover:shadow-lg transition-all"
              >
                <BookmarkIcon className="w-4 h-4" />
                <span className="hidden sm:inline">Save Trip</span>
              </button>
              <button
                onClick={() => router.push('/')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
              >
                <ArrowLeftIcon className="w-4 h-4" />
                <span className="hidden sm:inline">New Trip</span>
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm whitespace-nowrap transition-all ${
                    activeTab === tab.id
                      ? 'bg-primary text-primary-foreground shadow-md'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-[1400px] mx-auto px-6 py-8">
        <div className="animate-fadeIn">
          {activeTab === 'itinerary' && (
            <div className="max-w-4xl mx-auto">
              <ItineraryCard itinerary={itinerary} />
            </div>
          )}

          {activeTab === 'budget' && (
            <div className="max-w-4xl mx-auto">
              <BudgetCard budget={budget} />
            </div>
          )}

          {activeTab === 'bookings' && (
            <div className="max-w-4xl mx-auto">
              <BookingsCard
                bookings={bookings}
                origin={origin}
                destination={displayTitle}
                startDate={startDate}
                endDate={endDate}
              />
            </div>
          )}

          {activeTab === 'map' && (
            <div className="max-w-6xl mx-auto">
              <div className="glass-card rounded-2xl p-6 border border-border-subtle shadow-lg">
                <h2 className="text-2xl font-bold mb-6 text-card-foreground">Explore Locations</h2>
                <MapEmbed mapData={mapData} destination={displayTitle} />
              </div>
            </div>
          )}

          {activeTab === 'weather' && (
            <div className="max-w-4xl mx-auto">
              <WeatherCard weather={weather} destination={displayTitle} />
            </div>
          )}

          {activeTab === 'news' && (
            <div className="max-w-4xl mx-auto">
              <NewsCard news={news} destination={displayTitle} />
            </div>
          )}
        </div>
      </div>

      {/* Floating ChatBot */}
      <ChatBot currentTrip={result} />

      {/* Save Trip Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-background border border-border-subtle rounded-2xl shadow-2xl max-w-md w-full p-8 relative animate-fadeIn">
            <h2 className="text-2xl font-bold text-foreground mb-6">Save Your Trip</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Trip Name
                </label>
                <input
                  type="text"
                  value={tripName}
                  onChange={(e) => setTripName(e.target.value)}
                  className="w-full px-4 py-3 border border-border bg-input rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="My Amazing Trip"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Notes (optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-border bg-input rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  placeholder="Add any notes about this trip..."
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowSaveModal(false)}
                disabled={isSaving}
                className="flex-1 px-4 py-3 border border-border rounded-xl text-foreground hover:bg-muted transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveTrip}
                disabled={isSaving}
                className="flex-1 bg-gradient-to-br from-primary to-accent text-primary-foreground font-semibold py-3 px-6 rounded-xl transition-all hover:shadow-lg disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Trip'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultMode="signup"
      />
    </div>
  );
}
