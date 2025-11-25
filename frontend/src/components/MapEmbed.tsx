'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapAttraction } from '@/types';

// Fix Leaflet default marker icon issue
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  });
}

interface MapEmbedProps {
  mapData?: MapAttraction[];
  destination: string;
}

export default function MapEmbed({ mapData = [], destination }: MapEmbedProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!mapContainerRef.current || mapData.length === 0) return;

    // Get center coordinates from first attraction
    const centerLat = mapData[0].location?.lat || 0;
    const centerLng = mapData[0].location?.lng || 0;

    // Initialize map
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView([centerLat, centerLng], 13);

      // Add OpenStreetMap tiles (free!)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(mapRef.current);
    }

    // Clear existing markers
    mapRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        mapRef.current?.removeLayer(layer);
      }
    });

    // Add markers for each attraction
    mapData.forEach((place) => {
      if (place.location?.lat && place.location?.lng && mapRef.current) {
        const marker = L.marker([place.location.lat, place.location.lng])
          .bindPopup(`<strong>${place.name}</strong><br/>${place.type || 'Attraction'}`)
          .addTo(mapRef.current);
      }
    });

    // Cleanup on unmount
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [mapData]);

  if (!mapData || mapData.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-sm">
        <h3 className="text-xl mb-3 text-gray-800 dark:text-gray-100">🗺️ Map</h3>
        <div className="p-10 bg-gray-100 dark:bg-gray-800 rounded-lg text-center text-gray-600 dark:text-gray-400">
          No location data available for {destination}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-sm">
      <h3 className="text-xl mb-3 text-gray-800 dark:text-gray-100">🗺️ Top Attractions</h3>

      <div
        ref={mapContainerRef}
        className="h-[400px] w-full rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700"
      />

      <div className="mt-4">
        <strong className="text-sm text-gray-600 dark:text-gray-400">Places to Visit:</strong>
        <ul className="mt-2 ml-5 p-0">
          {mapData.map((p, i) => (
            <li key={i} className="text-sm text-gray-700 dark:text-gray-300 mb-1">
              {p.wiki ? (
                <a
                  href={p.wiki}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 underline font-medium"
                  title="Learn more on Wikipedia"
                >
                  {p.name}
                </a>
              ) : (
                p.name
              )}
              {' '}{p.type && <span className="text-gray-400">({p.type})</span>}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-md text-xs text-blue-900 dark:text-blue-300">
        📍 Powered by OpenStreetMap (free & open-source)
      </div>
    </div>
  );
}
