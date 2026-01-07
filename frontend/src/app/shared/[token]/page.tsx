'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import dynamic from 'next/dynamic';
import { API_ENDPOINTS } from '@/config/api';
import ItineraryCard from '@/components/ItineraryCard';
import BudgetCard from '@/components/BudgetCard';
import BookingsCard from '@/components/BookingsCard';
import WeatherCard from '@/components/WeatherCard';
import NewsCard from '@/components/NewsCard';
import {
  ArrowLeftIcon,
  MapPinIcon,
  CalendarDaysIcon,
  MapIcon,
  CloudIcon,
  NewspaperIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline';

const MapEmbed = dynamic(() => import('@/components/MapEmbed'), {
  ssr: false,
  loading: () => <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-md h-[600px] flex items-center justify-center text-gray-500">Loading map...</div>
});

type TabType = 'itinerary' | 'budget' | 'bookings' | 'map' | 'weather' | 'news';

interface Creator {
  username: string;
  profile_picture?: string;
}

export default function SharedTripPage() {
  const params = useParams();
  const router = useRouter();
  const token = params?.token as string;

  const [tripData, setTripData] = useState<any>(null);
  const [creator, setCreator] = useState<Creator | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('itinerary');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchSharedTrip();
    }
  }, [token]);

  const fetchSharedTrip = async () => {
    try {
      const response = await axios.get(API_ENDPOINTS.sharedTrip(token));

      const trip = response.data.trip;
      setCreator(response.data.creator);

      // Format trip data to match the structure expected by components
      setTripData({
        result: trip.data,
        country: trip.country,
        locations: trip.locations,
        days: trip.days,
        origin: trip.origin,
        startDate: trip.start_date,
        tripName: trip.trip_name
      });
    } catch (err: any) {
      console.error('Fetch shared trip error:', err);
      setError(err.response?.data?.error || 'Failed to load shared trip');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground">Loading trip...</div>
      </div>
    );
  }

  if (error || !tripData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-6">
        <div className="glass-card rounded-2xl p-12 border border-border-subtle shadow-lg text-center max-w-md">
          <div className="w-20 h-20 rounded-full bg-destructive/10 mx-auto mb-4 flex items-center justify-center">
            <MapPinIcon className="w-10 h-10 text-destructive" />
          </div>
          <h3 className="text-2xl font-bold text-card-foreground mb-2">
            Trip Not Found
          </h3>
          <p className="text-muted-foreground mb-6">
            {error || 'This trip link may be invalid or expired'}
          </p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-xl hover:shadow-lg transition-all font-semibold"
          >
            Plan Your Own Trip
          </button>
        </div>
      </div>
    );
  }

  // Display title - locations if specified, otherwise country
  const displayTitle = tripData.locations && tripData.locations !== 'AI Selected'
    ? tripData.locations
    : tripData.country;

  const tabs = [
    { id: 'itinerary' as TabType, name: 'Itinerary', icon: CalendarDaysIcon },
    { id: 'budget' as TabType, name: 'Budget', icon: CurrencyDollarIcon },
    { id: 'bookings' as TabType, name: 'Bookings', icon: BuildingOfficeIcon },
    { id: 'map' as TabType, name: 'Map', icon: MapIcon },
    { id: 'weather' as TabType, name: 'Weather', icon: CloudIcon },
    { id: 'news' as TabType, name: 'News', icon: NewspaperIcon }
  ];

  return (
    <div className="min-h-screen bg-background py-8 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header with Creator Info */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Plan Your Own Trip
          </button>

          {/* Shared By Banner */}
          {creator && (
            <div className="glass-card rounded-xl p-4 border border-primary/20 bg-primary/5 mb-4">
              <div className="flex items-center gap-3">
                {creator.profile_picture ? (
                  <img
                    src={creator.profile_picture}
                    alt={creator.username}
                    className="w-10 h-10 rounded-full"
                  />
                ) : (
                  <UserCircleIcon className="w-10 h-10 text-primary" />
                )}
                <div>
                  <p className="text-sm text-muted-foreground">Shared by</p>
                  <p className="font-semibold text-foreground">{creator.username}</p>
                </div>
              </div>
            </div>
          )}

          {/* Trip Title */}
          <h1 className="text-4xl font-bold bg-gradient-to-br from-foreground to-primary bg-clip-text text-transparent mb-2">
            {tripData.tripName || `Trip to ${tripData.country}`}
          </h1>

          {/* Trip Details */}
          <div className="flex flex-wrap items-center gap-4 text-muted-foreground">
            <div className="flex items-center gap-2">
              <MapPinIcon className="w-4 h-4" />
              <span>{tripData.locations && tripData.locations !== 'AI Selected' ? tripData.locations : tripData.country}</span>
            </div>
            <div className="flex items-center gap-2">
              <CalendarDaysIcon className="w-4 h-4" />
              <span>{tripData.days} {tripData.days === 1 ? 'day' : 'days'}</span>
            </div>
            {tripData.startDate && (
              <div className="flex items-center gap-2">
                <CalendarDaysIcon className="w-4 h-4" />
                <span>Starting {new Date(tripData.startDate).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-br from-primary to-accent text-primary-foreground shadow-lg'
                    : 'glass-card border border-border-subtle text-muted-foreground hover:text-foreground hover:shadow-md'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.name}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="mb-8">
          {activeTab === 'itinerary' && tripData.result?.itinerary && (
            <ItineraryCard itinerary={tripData.result.itinerary} />
          )}
          {activeTab === 'budget' && tripData.result?.budget && (
            <BudgetCard budget={tripData.result.budget} />
          )}
          {activeTab === 'bookings' && tripData.result?.bookings && (
            <BookingsCard bookings={tripData.result.bookings} />
          )}
          {activeTab === 'map' && tripData.result?.mapData && (
            <MapEmbed mapData={tripData.result.mapData} destination={displayTitle} />
          )}
          {activeTab === 'weather' && tripData.result?.weather && (
            <WeatherCard weather={tripData.result.weather} destination={displayTitle} />
          )}
          {activeTab === 'news' && tripData.result?.news && (
            <NewsCard news={tripData.result.news} destination={displayTitle} />
          )}
        </div>

        {/* CTA */}
        <div className="glass-card rounded-2xl p-8 border border-border-subtle shadow-lg text-center">
          <h3 className="text-2xl font-bold text-card-foreground mb-2">
            Plan Your Own Adventure
          </h3>
          <p className="text-muted-foreground mb-6">
            Create your personalized travel itinerary with AI-powered recommendations
          </p>
          <button
            onClick={() => router.push('/')}
            className="px-8 py-4 bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-xl hover:shadow-lg transition-all font-semibold text-lg"
          >
            Start Planning
          </button>
        </div>
      </div>
    </div>
  );
}
