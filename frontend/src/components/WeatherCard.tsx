'use client';

import { CloudIcon } from '@heroicons/react/24/outline';

interface WeatherForecast {
  location: string;
  latitude: number;
  longitude: number;
  timezone: string;
  forecast: {
    date: string;
    maxtemp_c: number;
    maxtemp_f: number;
    mintemp_c: number;
    mintemp_f: number;
    precipitation_sum: number;
    precipitation_probability: number;
    wind_speed_max: number;
    weather_code: number;
    condition: {
      text: string;
      icon: string;
    };
  }[];
}

interface WeatherCardProps {
  weather: WeatherForecast | null;
  destination: string;
}

export default function WeatherCard({ weather, destination }: WeatherCardProps) {
  if (!weather || !weather.forecast || weather.forecast.length === 0) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const today = weather.forecast[0];
  const upcomingDays = weather.forecast.slice(1);

  return (
    <div className="glass-card rounded-2xl p-6 border border-border-subtle shadow-lg">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
          <CloudIcon className="w-5 h-5 text-primary-foreground" />
        </div>
        <h3 className="text-xl font-bold text-card-foreground">
          Weather Forecast
        </h3>
      </div>

      {/* Today's Weather */}
      <div className="mb-5 pb-5 border-b border-border-subtle">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h4 className="text-lg font-semibold text-card-foreground mb-1">
              Today
            </h4>
            <p className="text-sm text-muted-foreground">{weather.location || destination}</p>
          </div>
          <div className="text-5xl">
            {today.condition.icon}
          </div>
        </div>
        <div className="flex items-start gap-6">
          <div>
            <div className="text-4xl font-bold text-primary">
              {Math.round(today.maxtemp_c)}°
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {Math.round(today.maxtemp_f)}°F
            </div>
          </div>
          <div className="flex-1 space-y-2">
            <p className="text-card-foreground font-semibold">
              {today.condition.text}
            </p>
            <div className="text-sm text-muted-foreground space-y-1">
              <p className="flex items-center gap-2">
                <span>🌡️</span>
                Low: {Math.round(today.mintemp_c)}°C / {Math.round(today.mintemp_f)}°F
              </p>
              <p className="flex items-center gap-2">
                <span>💨</span>
                Wind: {Math.round(today.wind_speed_max)} km/h
              </p>
              {today.precipitation_probability > 0 && (
                <p className="flex items-center gap-2 text-primary">
                  <span>☔</span>
                  Rain: {today.precipitation_probability}%
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Days */}
      {upcomingDays.length > 0 && (
        <div>
          <h5 className="text-sm font-semibold text-card-foreground mb-3">
            Upcoming Days
          </h5>
          <div className="space-y-3">
            {upcomingDays.map((day, index) => (
              <div
                key={index}
                className="p-4 rounded-xl border border-border-subtle bg-gradient-to-r from-muted/30 to-transparent hover:from-muted/50 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-card-foreground">
                    {formatDate(day.date)}
                  </span>
                  <div className="text-3xl">
                    {day.condition.icon}
                  </div>
                </div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex justify-between items-center">
                    <span>High:</span>
                    <span className="font-semibold text-card-foreground">
                      {Math.round(day.maxtemp_c)}°C / {Math.round(day.maxtemp_f)}°F
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Low:</span>
                    <span className="font-semibold text-card-foreground">
                      {Math.round(day.mintemp_c)}°C / {Math.round(day.mintemp_f)}°F
                    </span>
                  </div>
                  <p className="text-xs pt-1 border-t border-border-subtle">
                    {day.condition.text}
                  </p>
                  {day.precipitation_probability > 0 && (
                    <p className="text-xs text-primary flex items-center gap-1">
                      <span>☔</span>
                      {day.precipitation_probability}% chance of rain
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
