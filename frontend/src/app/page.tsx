'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import {
  MapPinIcon,
  CalendarIcon,
  ClockIcon,
  GlobeAltIcon,
  SparklesIcon,
  PaperAirplaneIcon
} from '@heroicons/react/24/outline';

const countries = [
  'United States', 'Canada', 'Mexico', 'United Kingdom', 'France', 'Germany', 'Italy', 'Spain',
  'Portugal', 'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Greece', 'Turkey', 'Japan',
  'China', 'South Korea', 'Thailand', 'Vietnam', 'Singapore', 'Malaysia', 'Indonesia',
  'Philippines', 'India', 'United Arab Emirates', 'Australia', 'New Zealand', 'Brazil',
  'Argentina', 'Chile', 'Peru', 'Colombia', 'South Africa', 'Egypt', 'Morocco'
];

// Popular origins for autofill (airports and cities)
const popularOrigins = [
  'LAX - Los Angeles',
  'SFO - San Francisco',
  'JFK - New York City',
  'ORD - Chicago',
  'DFW - Dallas',
  'ATL - Atlanta',
  'MIA - Miami',
  'SEA - Seattle',
  'BOS - Boston',
  'LHR - London',
  'CDG - Paris',
  'NRT - Tokyo',
  'HND - Tokyo',
  'SYD - Sydney',
  'DXB - Dubai',
  'Los Angeles',
  'San Francisco',
  'New York',
  'Chicago',
  'Dallas',
  'Atlanta',
  'Miami',
  'Seattle',
  'Boston',
  'London',
  'Paris',
  'Tokyo',
  'Sydney',
  'Dubai'
];

export default function SearchPage() {
  const [country, setCountry] = useState('Japan');
  const [locations, setLocations] = useState('');
  const [origin, setOrigin] = useState('');
  const [days, setDays] = useState(3);
  const [startDate, setStartDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [additionalDetails, setAdditionalDetails] = useState('');
  const [showDetailsBox, setShowDetailsBox] = useState(false);
  const router = useRouter();

  // Get user's current location and set as origin
  const useCurrentLocation = async () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      const { latitude, longitude } = position.coords;

      // Use reverse geocoding to get city name
      const response = await axios.get(`https://nominatim.openstreetmap.org/reverse`, {
        params: {
          lat: latitude,
          lon: longitude,
          format: 'json'
        },
        headers: {
          'User-Agent': 'AI-Travel-Planner/1.0'
        }
      });

      const address = response.data.address;
      const city = address.city || address.town || address.village || address.county;

      if (city) {
        setOrigin(city);
      } else {
        alert('Could not determine your city from your location');
      }
    } catch (error) {
      console.error('Error getting location:', error);
      alert('Could not get your location. Please enter it manually.');
    }
  };

  // Check if input is an airport code (3-4 uppercase letters)
  function isAirportCode(location: string): boolean {
    return /^[A-Z]{3,4}$/i.test(location.trim());
  }

  // Validate location using Nominatim API
  async function validateLocation(location: string, isOrigin: boolean = false): Promise<boolean> {
    try {
      // If it's an airport code (e.g., SFO, LAX, JFK), consider it valid for origin
      if (isOrigin && isAirportCode(location)) {
        return true;
      }

      const response = await axios.get(`https://nominatim.openstreetmap.org/search`, {
        params: {
          q: location,
          format: 'json',
          limit: 5,
          addressdetails: 1
        },
        headers: {
          'User-Agent': 'AI-Travel-Planner/1.0'
        }
      });

      if (!response.data || response.data.length === 0) {
        return false;
      }

      // Check if any result is a valid destination (city, town, state, country, etc.)
      // Filter out low-level places like bars, restaurants, buildings
      const validTypes = [
        'city', 'town', 'village', 'municipality',
        'state', 'province', 'region',
        'country', 'administrative',
        'county', 'district',
        'aerodrome', 'airport' // Accept airports
      ];

      const hasValidPlace = response.data.some((result: any) => {
        const type = result.type?.toLowerCase() || '';
        const placeClass = result.class?.toLowerCase() || '';
        const placeRank = result.place_rank || 0;

        // Accept if it's a valid type or has a high enough place_rank (lower is better for cities)
        return validTypes.some(validType => type.includes(validType) || placeClass.includes(validType))
               || placeRank <= 16; // Cities typically have place_rank <= 16
      });

      return hasValidPlace;
    } catch (error) {
      console.error('Location validation error:', error);
      return false;
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setValidationError('');

    try {
      // Validate country is provided
      if (!country) {
        setValidationError('Please select a country');
        setLoading(false);
        return;
      }

      const resp = await axios.post('http://localhost:4000/plan-trip', {
        country: country,
        locations: locations.trim() || undefined,
        days,
        origin: origin || 'Your City',
        additionalDetails: additionalDetails.trim() || undefined
      });

      // Store data in sessionStorage for the trip page
      sessionStorage.setItem('tripData', JSON.stringify({
        result: resp.data,
        country: country,
        locations: locations || 'AI Selected',
        days,
        origin: origin || 'Your City',
        startDate
      }));

      router.push('/trip');
    } catch (err: any) {
      alert('Failed to plan trip: ' + (err?.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-accent/5 to-secondary/10 dark:from-background dark:via-primary/5 dark:to-accent/10"></div>

      {/* Animated grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>

      {/* Glowing orbs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-pulse delay-1000"></div>

      <div className="relative max-w-2xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-border-subtle mb-4">
            <SparklesIcon className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium text-muted-foreground">AI-Powered Travel Planning</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-br from-foreground via-primary to-accent bg-clip-text text-transparent leading-tight">
            Travel Planner
          </h1>

          <p className="text-xl text-muted-foreground max-w-lg mx-auto">
            Craft your perfect journey with intelligent recommendations
          </p>
        </div>

        {/* Main Form Card */}
        <div className="glass-card rounded-2xl p-8 shadow-2xl border border-border-subtle relative overflow-hidden">
          {/* Subtle gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 pointer-events-none"></div>


        <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
          {/* Country Input */}
          <div className="group">
            <label className="flex items-center gap-2 mb-3 text-sm font-semibold text-card-foreground">
              <GlobeAltIcon className="w-5 h-5 text-primary" />
              Which country do you want to visit? *
            </label>
            <input
              type="text"
              list="countries-list"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              placeholder="e.g., Japan, New Zealand, Italy"
              required
              className="w-full px-4 py-4 border border-border bg-card rounded-xl text-card-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground hover:border-primary/50 shadow-sm"
            />
            <datalist id="countries-list">
              {countries.map((c) => (
                <option key={c} value={c} />
              ))}
            </datalist>
          </div>

          {/* Locations Input */}
          <div className="group">
            <label className="flex items-center gap-2 mb-3 text-sm font-semibold text-card-foreground">
              <MapPinIcon className="w-5 h-5 text-primary" />
              Specific Cities/Locations (Optional)
            </label>
            <input
              type="text"
              value={locations}
              onChange={(e) => setLocations(e.target.value)}
              placeholder="e.g., Auckland, Queenstown, Wellington"
              className="w-full px-4 py-4 border border-border bg-card rounded-xl text-card-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground hover:border-primary/50 shadow-sm"
            />
            <p className="mt-2 text-xs text-muted-foreground">
              Leave blank to let AI suggest cities, or enter specific locations separated by commas
            </p>
          </div>

          {/* Origin Input */}
          <div className="group">
            <label className="flex items-center justify-between mb-3 text-sm font-semibold text-card-foreground">
              <span className="flex items-center gap-2">
                <PaperAirplaneIcon className="w-5 h-5 text-primary" />
                Departing From
              </span>
              <button
                type="button"
                onClick={useCurrentLocation}
                className="text-xs text-primary hover:text-primary-hover transition-colors font-semibold flex items-center gap-1"
              >
                <MapPinIcon className="w-3 h-3" />
                Use My Location
              </button>
            </label>
            <input
              type="text"
              list="origins-list"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              placeholder="e.g., SFO, LAX, Los Angeles"
              className="w-full px-4 py-4 border border-border bg-card rounded-xl text-card-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground hover:border-primary/50 shadow-sm"
            />
            <datalist id="origins-list">
              {popularOrigins.map((origin) => (
                <option key={origin} value={origin} />
              ))}
            </datalist>
          </div>

          {/* Date & Duration Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="group">
              <label className="flex items-center gap-2 mb-3 text-sm font-semibold text-card-foreground">
                <CalendarIcon className="w-5 h-5 text-primary" />
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                required
                className="w-full px-4 py-4 border border-border bg-card rounded-xl text-card-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all shadow-sm"
              />
            </div>
            <div className="group">
              <label className="flex items-center gap-2 mb-3 text-sm font-semibold text-card-foreground">
                <ClockIcon className="w-5 h-5 text-primary" />
                Duration (days)
              </label>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                value={days}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d+$/.test(value)) {
                    const num = value === '' ? 0 : Number(value);
                    if (num >= 0 && num <= 30) {
                      setDays(num);
                    }
                  }
                }}
                onBlur={(e) => {
                  if (e.target.value === '' || Number(e.target.value) === 0) {
                    setDays(1);
                  }
                }}
                placeholder="1-30 days"
                required
                className="w-full px-4 py-4 border border-border bg-card rounded-xl text-card-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground hover:border-primary/50 shadow-sm"
              />
            </div>
          </div>

          {/* Additional Details Section */}
          <div className="border-t border-border-subtle pt-4">
            <button
              type="button"
              onClick={() => setShowDetailsBox(!showDetailsBox)}
              className="flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary-hover transition-colors mb-3"
            >
              <SparklesIcon className="w-4 h-4" />
              {showDetailsBox ? 'Hide' : 'Add'} Trip Preferences (Optional)
              <span className="text-xs font-normal text-muted-foreground">
                {showDetailsBox ? '▲' : '▼'}
              </span>
            </button>

            {showDetailsBox && (
              <div className="space-y-3 p-4 rounded-xl bg-gradient-to-br from-primary/5 to-accent/5 border border-border-subtle">
                <p className="text-xs text-muted-foreground">
                  Tell us about any existing plans, tickets, or specific activities you want to include:
                </p>
                <textarea
                  value={additionalDetails}
                  onChange={(e) => setAdditionalDetails(e.target.value)}
                  placeholder="Examples:&#10;• I have tickets to Universal Studios on Day 2&#10;• I want to visit art museums and local cafes&#10;• I'm interested in trying authentic street food&#10;• I have dinner reservations at [restaurant] on Day 1"
                  rows={6}
                  className="w-full px-4 py-3 border border-border bg-card rounded-xl text-card-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder:text-muted-foreground resize-none text-sm"
                />
                {additionalDetails && (
                  <div className="flex items-center gap-2 text-xs text-success">
                    <SparklesIcon className="w-4 h-4" />
                    AI will incorporate these preferences into your itinerary
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Validation Error */}
          {validationError && (
            <div className="p-4 glass-card rounded-xl border border-destructive/50 bg-destructive/10">
              <p className="text-sm text-destructive font-medium">{validationError}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full relative group overflow-hidden bg-gradient-to-r from-primary via-primary-hover to-accent text-primary-foreground font-semibold py-5 px-6 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
          >
            {/* Animated gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-accent via-primary to-primary-hover opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

            <span className="relative z-10 flex items-center justify-center gap-2">
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Crafting your journey...
                </>
              ) : (
                <>
                  <SparklesIcon className="w-5 h-5" />
                  Plan My Trip
                </>
              )}
            </span>
          </button>
        </form>
        </div>

        {/* Info Card */}
        <div className="mt-6 p-5 glass-card rounded-xl border border-border-subtle space-y-2">
          <p className="text-sm text-muted-foreground">
            <span className="font-semibold text-primary">Pro Tip:</span> Include state and country for precise recommendations (e.g., "Seattle, Washington, USA")
          </p>
          <p className="text-xs text-muted-foreground">
            <span className="font-semibold text-accent">New!</span> Use the trip preferences section to tell us about existing tickets, reservations, or specific interests. The AI will create a personalized itinerary around your plans.
          </p>
        </div>
      </div>
    </div>
  );
}
