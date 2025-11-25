'use client';

import { Bookings } from '@/types';

interface BookingsCardProps {
  bookings: Bookings | null;
  origin?: string;
  destination?: string;
  startDate?: string;
  endDate?: string;
}

export default function BookingsCard({ bookings, origin, destination, startDate, endDate }: BookingsCardProps) {
  if (!bookings) return null;

  // Helper function to build booking URLs with parameters
  const buildHotelUrl = (baseUrl: string, siteName: string) => {
    if (!destination || !startDate || !endDate) return baseUrl;

    const checkIn = startDate;
    const checkOut = endDate;

    // Different URL formats for different booking sites with direct search
    if (siteName === 'Booking.com') {
      // Booking.com direct search with auto-submit
      return `https://www.booking.com/searchresults.html?ss=${encodeURIComponent(destination)}&checkin=${checkIn}&checkout=${checkOut}&group_adults=2&no_rooms=1&group_children=0`;
    } else if (siteName === 'Hotels.com') {
      // Hotels.com direct search
      return `https://www.hotels.com/search.do?q-destination=${encodeURIComponent(destination)}&q-check-in=${checkIn}&q-check-out=${checkOut}&q-rooms=1&q-room-0-adults=2&q-room-0-children=0`;
    } else if (siteName === 'Expedia') {
      // Expedia direct search
      return `https://www.expedia.com/Hotel-Search?destination=${encodeURIComponent(destination)}&startDate=${checkIn}&endDate=${checkOut}&adults=2`;
    }
    return baseUrl;
  };

  const buildFlightUrl = (baseUrl: string, siteName: string) => {
    if (!origin || !destination || !startDate) return baseUrl;

    // Parse airport codes or city names
    const originCode = origin.toUpperCase().includes(',') ? origin.split(',')[0].trim() : origin.trim();
    const destCode = destination.toUpperCase().includes(',') ? destination.split(',')[0].trim() : destination.trim();

    // Different URL formats for different flight search sites with direct search
    if (siteName === 'Google Flights') {
      // Google Flights direct search - uses their URL structure
      return `https://www.google.com/travel/flights?q=Flights%20to%20${encodeURIComponent(destCode)}%20from%20${encodeURIComponent(originCode)}%20on%20${startDate}&curr=USD`;
    } else if (siteName === 'Kayak') {
      // Kayak direct search - better URL structure
      return `https://www.kayak.com/flights/${encodeURIComponent(originCode)}-${encodeURIComponent(destCode)}/${startDate}?sort=bestflight_a`;
    } else if (siteName === 'Skyscanner') {
      // Skyscanner direct search with proper formatting
      const dateFormatted = startDate.replace(/-/g, '');
      return `https://www.skyscanner.com/transport/flights/${encodeURIComponent(originCode)}/${encodeURIComponent(destCode)}/${dateFormatted}/?adults=1&adultsv2=1&cabinclass=economy&children=0&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0`;
    }
    return baseUrl;
  };

  return (
    <div className="mb-5">
      <h3 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        🏨 Booking Options
      </h3>

      {bookings.hotels && bookings.hotels.length > 0 && (
        <div className="mb-5">
          <h4 className="text-lg mb-3 text-blue-600 dark:text-blue-400 border-l-4 border-blue-600 pl-3">
            Hotel Websites
          </h4>
          <div className="grid gap-3">
            {bookings.hotels.map((h, i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm flex justify-between items-center"
              >
                <div className="flex-1">
                  <div className="text-base font-bold text-gray-800 dark:text-gray-100 mb-1.5">
                    {h.name}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {h.description}
                  </div>
                </div>
                <a
                  href={buildHotelUrl(h.link, h.name)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-bold transition-colors ml-4"
                >
                  Search Hotels →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {bookings.flights && bookings.flights.length > 0 && (
        <div>
          <h4 className="text-lg mb-3 text-blue-600 dark:text-blue-400 border-l-4 border-blue-600 pl-3">
            Flight Websites
          </h4>
          <div className="grid gap-3">
            {bookings.flights.map((f, i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm flex justify-between items-center"
              >
                <div className="flex-1">
                  <div className="text-base font-bold text-gray-800 dark:text-gray-100 mb-1.5">
                    {f.airline || 'Flight Search'}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Search flights from {origin || f.origin || 'Your City'} to {destination || f.destination}
                  </div>
                </div>
                <a
                  href={buildFlightUrl(f.link, f.airline || 'Google Flights')}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-bold transition-colors ml-4"
                >
                  Search Flights →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {(!bookings.hotels || bookings.hotels.length === 0) &&
        (!bookings.flights || bookings.flights.length === 0) && (
          <div className="p-5 bg-gray-100 dark:bg-gray-800 rounded-lg text-center text-gray-600 dark:text-gray-400">
            No booking options available at the moment
          </div>
        )}
    </div>
  );
}
