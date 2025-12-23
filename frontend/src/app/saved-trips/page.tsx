'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import {
  MapPinIcon,
  CalendarDaysIcon,
  TrashIcon,
  HeartIcon,
  ArrowLeftIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

interface SavedTrip {
  id: number;
  trip_name: string;
  country: string;
  locations?: string;
  days: number;
  origin?: string;
  start_date?: string;
  trip_pace?: string;
  notes?: string;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}

export default function SavedTripsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [trips, setTrips] = useState<SavedTrip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/');
    }

    if (user) {
      fetchTrips();
    }
  }, [user, authLoading, router]);

  const fetchTrips = async () => {
    try {
      const response = await axios.get('http://localhost:4000/api/auth/trips', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      setTrips(response.data.trips);
    } catch (err: any) {
      console.error('Fetch trips error:', err);
      setError('Failed to load trips');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleFavorite = async (tripId: number, currentFavorite: boolean) => {
    try {
      await axios.put(
        `http://localhost:4000/api/auth/trips/${tripId}`,
        { is_favorite: !currentFavorite },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          }
        }
      );

      // Update local state
      setTrips(trips.map(trip =>
        trip.id === tripId ? { ...trip, is_favorite: !currentFavorite } : trip
      ));
    } catch (err) {
      console.error('Toggle favorite error:', err);
    }
  };

  const deleteTrip = async (tripId: number) => {
    if (!confirm('Are you sure you want to delete this trip?')) return;

    try {
      await axios.delete(`http://localhost:4000/api/auth/trips/${tripId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      setTrips(trips.filter(trip => trip.id !== tripId));
    } catch (err) {
      console.error('Delete trip error:', err);
      alert('Failed to delete trip');
    }
  };

  const viewTrip = async (tripId: number) => {
    try {
      const response = await axios.get(`http://localhost:4000/api/auth/trips/${tripId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      const trip = response.data.trip;

      // Store in session storage and navigate to trip page
      const tripData = {
        result: trip.data,
        country: trip.country,
        locations: trip.locations,
        days: trip.days,
        origin: trip.origin,
        startDate: trip.start_date
      };

      sessionStorage.setItem('tripData', JSON.stringify(tripData));
      router.push('/trip');
    } catch (err) {
      console.error('View trip error:', err);
      alert('Failed to load trip');
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground">Loading trips...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Back to Home
          </button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-br from-foreground to-primary bg-clip-text text-transparent mb-2">
                My Saved Trips
              </h1>
              <p className="text-muted-foreground">
                {trips.length} {trips.length === 1 ? 'trip' : 'trips'} saved
              </p>
            </div>

            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 px-5 py-3 bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-xl hover:shadow-lg transition-all hover:scale-[1.02]"
            >
              <PlusIcon className="w-5 h-5" />
              <span className="font-semibold">Plan New Trip</span>
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-xl text-destructive">
            {error}
          </div>
        )}

        {/* Trips Grid */}
        {trips.length === 0 ? (
          <div className="glass-card rounded-2xl p-12 border border-border-subtle shadow-lg text-center">
            <div className="w-20 h-20 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
              <MapPinIcon className="w-10 h-10 text-muted-foreground" />
            </div>
            <h3 className="text-2xl font-bold text-card-foreground mb-2">
              No trips saved yet
            </h3>
            <p className="text-muted-foreground mb-6">
              Start planning your next adventure and save it to your collection
            </p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-xl hover:shadow-lg transition-all font-semibold"
            >
              Plan Your First Trip
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trips.map((trip) => (
              <div
                key={trip.id}
                className="glass-card rounded-2xl overflow-hidden border border-border-subtle shadow-lg hover:shadow-xl transition-all group cursor-pointer"
                onClick={() => viewTrip(trip.id)}
              >
                {/* Trip Header Image */}
                <div className="relative h-40 overflow-hidden bg-gradient-to-br from-primary/20 to-accent/20">
                  <img
                    src={`https://source.unsplash.com/800x400/?${encodeURIComponent(trip.country)},travel,landmark`}
                    alt={trip.country}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>

                  {/* Favorite button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(trip.id, trip.is_favorite);
                    }}
                    className="absolute top-3 right-3 p-2 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/30 transition-colors"
                  >
                    {trip.is_favorite ? (
                      <HeartSolidIcon className="w-5 h-5 text-red-500" />
                    ) : (
                      <HeartIcon className="w-5 h-5 text-white" />
                    )}
                  </button>

                  {/* Trip name */}
                  <div className="absolute bottom-3 left-4 right-4">
                    <h3 className="text-lg font-bold text-white truncate">
                      {trip.trip_name}
                    </h3>
                  </div>
                </div>

                {/* Trip Info */}
                <div className="p-5">
                  <div className="space-y-3 mb-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <MapPinIcon className="w-4 h-4 text-primary" />
                      <span className="font-medium text-foreground">
                        {trip.locations || trip.country}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <CalendarDaysIcon className="w-4 h-4" />
                        <span>{trip.days} {trip.days === 1 ? 'day' : 'days'}</span>
                      </div>
                      {trip.start_date && (
                        <span className="text-xs">
                          {new Date(trip.start_date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                          })}
                        </span>
                      )}
                    </div>

                    {trip.notes && (
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {trip.notes}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
                    <span className="text-xs text-muted-foreground">
                      Saved {new Date(trip.created_at).toLocaleDateString()}
                    </span>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteTrip(trip.id);
                      }}
                      className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
                      aria-label="Delete trip"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
