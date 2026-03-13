'use client';

import { Itinerary, DayItinerary } from '@/types';
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

// Helper function to parse markdown bold syntax (**text**)
function parseMarkdownBold(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  const boldRegex = /\*\*(.*?)\*\*/g;
  let lastIndex = 0;
  let match;
  let matchIndex = 0;

  while ((match = boldRegex.exec(text)) !== null) {
    // Add text before the bold part
    if (match.index > lastIndex) {
      parts.push(
        <span key={`text-${matchIndex}`}>{text.substring(lastIndex, match.index)}</span>
      );
    }
    // Add the bold part
    parts.push(
      <strong key={`bold-${matchIndex}`} className="font-bold text-card-foreground">
        {match[1]}
      </strong>
    );
    lastIndex = match.index + match[0].length;
    matchIndex++;
  }

  // Add remaining text after last bold part
  if (lastIndex < text.length) {
    parts.push(
      <span key={`text-${matchIndex}`}>{text.substring(lastIndex)}</span>
    );
  }

  return parts.length > 0 ? <>{parts}</> : text;
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {Object.keys(itinerary)
        .filter((key) => key !== 'raw')
        .sort((a, b) => {
          const numA = parseInt(a.replace('day', ''));
          const numB = parseInt(b.replace('day', ''));
          return numA - numB;
        })
        .map((dayKey) => {
          const day = itinerary[dayKey] as DayItinerary;
          const dayNumber = dayKey.replace('day', '');

          return (
            <div
              key={dayKey}
              className="glass-card rounded-2xl overflow-hidden border border-border-subtle shadow-lg hover:shadow-xl transition-all group"
            >
              {/* Day Header */}
              <div className="px-6 pt-6 pb-4 border-b border-border-subtle">
                <div className="flex items-center justify-between">
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
                    </div>
                  )}
                </div>
              </div>

              {/* Day Content */}
              <div className="p-6">

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
                      <span>{parseMarkdownBold(day.transportation.method)}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="font-semibold min-w-[80px]">Duration:</span>
                      <span>{parseMarkdownBold(day.transportation.duration)}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <CurrencyDollarIcon className="w-4 h-4 mt-0.5" />
                      <span className="font-semibold min-w-[70px]">Cost:</span>
                      <span>{parseMarkdownBold(day.transportation.cost_local)}{day.transportation.cost_usd && ` (${parseMarkdownBold(day.transportation.cost_usd)})`}</span>
                    </div>
                    {day.transportation.travel_note && (
                      <p className="text-xs italic pt-2 border-t border-border-subtle">{parseMarkdownBold(day.transportation.travel_note)}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Morning */}
              {day.morning && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-lg bg-warning/10 flex items-center justify-center">
                      <SunIcon className="w-4 h-4 text-warning" />
                    </div>
                    <span className="text-sm font-bold text-card-foreground">Morning</span>
                  </div>
                  {Array.isArray(day.morning) ? (
                    <ul className="list-disc ml-9 space-y-1.5 text-sm text-muted-foreground">
                      {day.morning.map((item, i) => {
                        if (typeof item === 'string') {
                          return <li key={i} className="leading-relaxed">{parseMarkdownBold(item)}</li>;
                        }

                        if (item.wiki && item.attractionName) {
                          const attractionName = item.attractionName;
                          const indexOfAttraction = item.text.indexOf(attractionName);

                          if (indexOfAttraction !== -1) {
                            const beforeAttraction = item.text.substring(0, indexOfAttraction);
                            const afterAttraction = item.text.substring(indexOfAttraction + attractionName.length);

                            return (
                              <li key={i} className="leading-relaxed">
                                {parseMarkdownBold(beforeAttraction)}
                                <a
                                  href={item.wiki}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary-hover underline font-semibold transition-colors"
                                  title="Learn more on Wikipedia"
                                >
                                  {attractionName}
                                </a>
                                {parseMarkdownBold(afterAttraction)}
                              </li>
                            );
                          }
                        }

                        return <li key={i} className="leading-relaxed">{parseMarkdownBold(item.text)}</li>;
                      })}
                    </ul>
                  ) : (
                    <p className="ml-9 text-sm leading-relaxed text-muted-foreground">
                      {parseMarkdownBold(day.morning as string)}
                    </p>
                  )}
                </div>
              )}

              {/* Afternoon */}
              {day.afternoon && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                      <SunIcon className="w-4 h-4 text-primary" />
                    </div>
                    <span className="text-sm font-bold text-card-foreground">Afternoon</span>
                  </div>
                  {Array.isArray(day.afternoon) ? (
                    <ul className="list-disc ml-9 space-y-1.5 text-sm text-muted-foreground">
                      {day.afternoon.map((item, i) => {
                        if (typeof item === 'string') {
                          return <li key={i} className="leading-relaxed">{parseMarkdownBold(item)}</li>;
                        }

                        if (item.wiki && item.attractionName) {
                          const attractionName = item.attractionName;
                          const indexOfAttraction = item.text.indexOf(attractionName);

                          if (indexOfAttraction !== -1) {
                            const beforeAttraction = item.text.substring(0, indexOfAttraction);
                            const afterAttraction = item.text.substring(indexOfAttraction + attractionName.length);

                            return (
                              <li key={i} className="leading-relaxed">
                                {parseMarkdownBold(beforeAttraction)}
                                <a
                                  href={item.wiki}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary-hover underline font-semibold transition-colors"
                                  title="Learn more on Wikipedia"
                                >
                                  {attractionName}
                                </a>
                                {parseMarkdownBold(afterAttraction)}
                              </li>
                            );
                          }
                        }

                        return <li key={i} className="leading-relaxed">{parseMarkdownBold(item.text)}</li>;
                      })}
                    </ul>
                  ) : (
                    <p className="ml-9 text-sm leading-relaxed text-muted-foreground">
                      {parseMarkdownBold(day.afternoon as string)}
                    </p>
                  )}
                </div>
              )}

              {/* Evening */}
              {day.evening && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center">
                      <MoonIcon className="w-4 h-4 text-accent" />
                    </div>
                    <span className="text-sm font-bold text-card-foreground">Evening</span>
                  </div>
                  {Array.isArray(day.evening) ? (
                    <ul className="list-disc ml-9 space-y-1.5 text-sm text-muted-foreground">
                      {day.evening.map((item, i) => {
                        if (typeof item === 'string') {
                          return <li key={i} className="leading-relaxed">{parseMarkdownBold(item)}</li>;
                        }

                        if (item.wiki && item.attractionName) {
                          const attractionName = item.attractionName;
                          const indexOfAttraction = item.text.indexOf(attractionName);

                          if (indexOfAttraction !== -1) {
                            const beforeAttraction = item.text.substring(0, indexOfAttraction);
                            const afterAttraction = item.text.substring(indexOfAttraction + attractionName.length);

                            return (
                              <li key={i} className="leading-relaxed">
                                {parseMarkdownBold(beforeAttraction)}
                                <a
                                  href={item.wiki}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary-hover underline font-semibold transition-colors"
                                  title="Learn more on Wikipedia"
                                >
                                  {attractionName}
                                </a>
                                {parseMarkdownBold(afterAttraction)}
                              </li>
                            );
                          }
                        }

                        return <li key={i} className="leading-relaxed">{parseMarkdownBold(item.text)}</li>;
                      })}
                    </ul>
                  ) : (
                    <p className="ml-9 text-sm leading-relaxed text-muted-foreground">
                      {parseMarkdownBold(day.evening as string)}
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
            </div>
          );
        })}
      </div>
    </div>
  );
}
