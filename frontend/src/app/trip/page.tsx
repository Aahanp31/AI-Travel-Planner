'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import ItineraryCard from '@/components/ItineraryCard';
import BudgetCard from '@/components/BudgetCard';
import BookingsCard from '@/components/BookingsCard';
import WeatherCard from '@/components/WeatherCard';
import NewsCard from '@/components/NewsCard';
import { TripResponse } from '@/types';
import { ArrowLeftIcon, MapPinIcon, ClockIcon } from '@heroicons/react/24/outline';

// Import MapEmbed dynamically to avoid SSR issues with Leaflet
const MapEmbed = dynamic(() => import('@/components/MapEmbed'), {
  ssr: false,
  loading: () => <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-md h-[600px] flex items-center justify-center text-gray-500">Loading map...</div>
});

export default function TripPage() {
  const router = useRouter();
  const [tripData, setTripData] = useState<any>(null);

  useEffect(() => {
    const data = sessionStorage.getItem('tripData');
    if (data) {
      setTripData(JSON.parse(data));
    }
  }, []);

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

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-accent/5 to-primary/5"></div>
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:32px_32px]"></div>

      <div className="relative max-w-[1400px] mx-auto p-6">
        {/* Header Card */}
        <div className="glass-card p-6 rounded-2xl mb-6 shadow-lg border border-border-subtle">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                  <MapPinIcon className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-br from-foreground to-primary bg-clip-text text-transparent">
                    {displayTitle}
                  </h1>
                  {displaySubtitle && (
                    <p className="text-sm text-muted-foreground mt-1">{displaySubtitle}</p>
                  )}
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground ml-15">
                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-muted/50">
                  <ClockIcon className="w-4 h-4" />
                  {days} day{days > 1 ? 's' : ''}
                </span>
                {origin && origin !== 'Your City' && (
                  <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-muted/50">
                    From {origin}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={() => router.push('/')}
              className="group flex items-center gap-2 px-5 py-3 rounded-xl border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-all font-semibold"
            >
              <ArrowLeftIcon className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              Plan Another Trip
            </button>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_420px] gap-6">
          <div className="space-y-6">
            <ItineraryCard itinerary={itinerary} />
            <BudgetCard budget={budget} />
            <BookingsCard
              bookings={bookings}
              origin={origin}
              destination={displayTitle}
              startDate={startDate}
              endDate={endDate}
            />
          </div>

          <div className="space-y-6">
            <WeatherCard weather={weather} destination={displayTitle} />
            <MapEmbed mapData={mapData} destination={displayTitle} />
            <NewsCard news={news} destination={displayTitle} />
          </div>
        </div>
      </div>
    </div>
  );
}
