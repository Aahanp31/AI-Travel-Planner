'use client';

import { Itinerary } from '@/types';
import {
  MapPinIcon,
  SunIcon,
  MoonIcon,
  CalendarIcon,
  TruckIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

interface ItineraryCardProps {
  itinerary: Itinerary | null;
}

export default function ItineraryCard({ itinerary }: ItineraryCardProps) {
  if (!itinerary) return null;

  if (itinerary.raw) {
    return (
      <div className="glass-card rounded-2xl p-6 border border-border-subtle shadow-lg">
        <pre className="whitespace-pre-wrap text-card-foreground font-mono text-sm">
          {itinerary.raw}
        </pre>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
          <CalendarIcon className="w-5 h-5 text-primary-foreground" />
        </div>
        <h2 className="text-3xl font-bold bg-gradient-to-br from-foreground to-primary bg-clip-text text-transparent">
          Your Itinerary
        </h2>
      </div>
      {Object.keys(itinerary)
        .sort((a, b) => {
          const numA = parseInt(a.replace('day', ''));
          const numB = parseInt(b.replace('day', ''));
          return numA - numB;
        })
        .map((dayKey) => {
          const day = itinerary[dayKey];
          const dayNumber = dayKey.replace('day', '');

          return (
            <div
              key={dayKey}
              className="glass-card rounded-2xl p-6 mb-5 border border-border-subtle shadow-lg hover:shadow-xl transition-shadow group"
            >
              {/* Day Header */}
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-border-subtle">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center font-bold text-primary">
                    {dayNumber}
                  </div>
                  <h3 className="text-2xl font-bold text-card-foreground">
                    Day {dayNumber}
                  </h3>
                </div>
                {day.location && (
                  <div className="flex items-center gap-2">
                    <MapPinIcon className="w-5 h-5 text-primary" />
                    <span className="text-sm font-medium text-muted-foreground">{day.location}</span>
                    {day.location_wiki && (
                      <a
                        href={day.location_wiki}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary-hover underline text-xs font-semibold transition-colors"
                        title="Learn more on Wikipedia"
                      >
                        Wiki
                      </a>
                    )}
                  </div>
                )}
              </div>

              {/* Transportation */}
              {day.transportation && (
                <div className="mb-6 p-5 rounded-xl border-l-4 border-primary bg-gradient-to-r from-primary/10 to-transparent">
                  <div className="flex items-center gap-2 mb-3">
                    <TruckIcon className="w-5 h-5 text-primary" />
                    <span className="text-sm font-bold text-card-foreground">
                      Transportation to {day.location}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-start gap-2">
                      <span className="font-semibold min-w-[80px]">Method:</span>
                      <span>{day.transportation.method}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="font-semibold min-w-[80px]">Duration:</span>
                      <span>{day.transportation.duration}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <CurrencyDollarIcon className="w-4 h-4 mt-0.5" />
                      <span className="font-semibold min-w-[70px]">Cost:</span>
                      <span>{day.transportation.cost_local}{day.transportation.cost_usd && ` (${day.transportation.cost_usd})`}</span>
                    </div>
                    {day.transportation.travel_note && (
                      <p className="text-xs italic pt-2 border-t border-border-subtle">{day.transportation.travel_note}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Morning */}
              {day.morning && (
                <div className="mb-5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-warning/20 flex items-center justify-center">
                      <SunIcon className="w-4 h-4 text-warning" />
                    </div>
                    <span className="text-sm font-bold text-card-foreground">Morning</span>
                  </div>
                  {Array.isArray(day.morning) ? (
                    <ul className="list-disc list-outside ml-6 space-y-2 leading-relaxed text-muted-foreground marker:text-warning">
                      {day.morning.map((item, i) => {
                        if (typeof item === 'string') {
                          return <li key={i} className="pl-1">{item}</li>;
                        }

                        // If there's a wiki link, make the attraction name clickable
                        if (item.wiki && item.attractionName) {
                          // Use the exact attraction name provided by the backend
                          const attractionName = item.attractionName;
                          const indexOfAttraction = item.text.indexOf(attractionName);

                          if (indexOfAttraction !== -1) {
                            const beforeAttraction = item.text.substring(0, indexOfAttraction);
                            const afterAttraction = item.text.substring(indexOfAttraction + attractionName.length);

                            return (
                              <li key={i} className="pl-1">
                                {beforeAttraction}
                                <a
                                  href={item.wiki}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary-hover underline font-semibold transition-colors"
                                  title="Learn more on Wikipedia"
                                >
                                  {attractionName}
                                </a>
                                {afterAttraction}
                              </li>
                            );
                          }
                        }

                        // Fallback: just show the text
                        return <li key={i} className="pl-1">{item.text}</li>;
                      })}
                    </ul>
                  ) : (
                    <p className="m-0 leading-relaxed text-muted-foreground">
                      {day.morning}
                    </p>
                  )}
                </div>
              )}

              {/* Afternoon */}
              {day.afternoon && (
                <div className="mb-5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                      <SunIcon className="w-4 h-4 text-primary" />
                    </div>
                    <span className="text-sm font-bold text-card-foreground">Afternoon</span>
                  </div>
                  {Array.isArray(day.afternoon) ? (
                    <ul className="list-disc list-outside ml-6 space-y-2 leading-relaxed text-muted-foreground marker:text-primary">
                      {day.afternoon.map((item, i) => {
                        if (typeof item === 'string') {
                          return <li key={i} className="pl-1">{item}</li>;
                        }

                        // If there's a wiki link, make the attraction name clickable
                        if (item.wiki && item.attractionName) {
                          // Use the exact attraction name provided by the backend
                          const attractionName = item.attractionName;
                          const indexOfAttraction = item.text.indexOf(attractionName);

                          if (indexOfAttraction !== -1) {
                            const beforeAttraction = item.text.substring(0, indexOfAttraction);
                            const afterAttraction = item.text.substring(indexOfAttraction + attractionName.length);

                            return (
                              <li key={i} className="pl-1">
                                {beforeAttraction}
                                <a
                                  href={item.wiki}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary-hover underline font-semibold transition-colors"
                                  title="Learn more on Wikipedia"
                                >
                                  {attractionName}
                                </a>
                                {afterAttraction}
                              </li>
                            );
                          }
                        }

                        // Fallback: just show the text
                        return <li key={i} className="pl-1">{item.text}</li>;
                      })}
                    </ul>
                  ) : (
                    <p className="m-0 leading-relaxed text-muted-foreground">
                      {day.afternoon}
                    </p>
                  )}
                </div>
              )}

              {/* Evening */}
              {day.evening && (
                <div className="mb-5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
                      <MoonIcon className="w-4 h-4 text-accent" />
                    </div>
                    <span className="text-sm font-bold text-card-foreground">Evening</span>
                  </div>
                  {Array.isArray(day.evening) ? (
                    <ul className="list-disc list-outside ml-6 space-y-2 leading-relaxed text-muted-foreground marker:text-accent">
                      {day.evening.map((item, i) => {
                        if (typeof item === 'string') {
                          return <li key={i} className="pl-1">{item}</li>;
                        }

                        // If there's a wiki link, make the attraction name clickable
                        if (item.wiki && item.attractionName) {
                          // Use the exact attraction name provided by the backend
                          const attractionName = item.attractionName;
                          const indexOfAttraction = item.text.indexOf(attractionName);

                          if (indexOfAttraction !== -1) {
                            const beforeAttraction = item.text.substring(0, indexOfAttraction);
                            const afterAttraction = item.text.substring(indexOfAttraction + attractionName.length);

                            return (
                              <li key={i} className="pl-1">
                                {beforeAttraction}
                                <a
                                  href={item.wiki}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary-hover underline font-semibold transition-colors"
                                  title="Learn more on Wikipedia"
                                >
                                  {attractionName}
                                </a>
                                {afterAttraction}
                              </li>
                            );
                          }
                        }

                        // Fallback: just show the text
                        return <li key={i} className="pl-1">{item.text}</li>;
                      })}
                    </ul>
                  ) : (
                    <p className="m-0 leading-relaxed text-muted-foreground">
                      {day.evening}
                    </p>
                  )}
                </div>
              )}

              {/* Food & Cultural Info */}
              <div className="mt-6 pt-6 border-t border-dashed border-border-subtle grid grid-cols-1 md:grid-cols-2 gap-4">
                {(day.food_recommendation || day.local_food_recommendation) && (
                  <div className="p-4 rounded-xl border border-warning/30 bg-gradient-to-br from-warning/10 to-transparent">
                    <div className="text-xs font-bold text-warning mb-2">
                      Food Recommendation
                    </div>
                    <p className="m-0 text-xs leading-relaxed text-muted-foreground">
                      {day.food_recommendation || day.local_food_recommendation}
                    </p>
                  </div>
                )}

                {day.cultural_highlight && (
                  <div className="p-4 rounded-xl border border-primary/30 bg-gradient-to-br from-primary/10 to-transparent">
                    <div className="text-xs font-bold text-primary mb-2">
                      Cultural Highlight
                    </div>
                    <p className="m-0 text-xs leading-relaxed text-muted-foreground">
                      {day.cultural_highlight}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
    </div>
  );
}
