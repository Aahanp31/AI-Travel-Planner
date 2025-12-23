export interface TripRequest {
  destination: string;
  days: number;
  origin?: string;
}

export interface Transportation {
  method: string;
  duration: string;
  cost_local: string;
  cost_usd?: string;
  travel_note: string;
}

export interface Activity {
  text: string;
  wiki?: string;
  attractionName?: string;
}

export interface DayItinerary {
  location?: string;
  location_wiki?: string;
  transportation?: Transportation;
  morning?: string | string[] | Activity[];
  afternoon?: string | string[] | Activity[];
  evening?: string | string[] | Activity[];
  food_recommendation?: string;
  local_food_recommendation?: string;
  cultural_highlight?: string;
}

export interface Itinerary {
  raw?: string;
  [key: string]: DayItinerary | string | undefined;
}

export interface Budget {
  city?: string;
  days?: number;
  destination_currency_code?: string;
  destination_symbol?: string;
  origin_currency_code?: string;
  origin_symbol?: string;
  exchange_rate?: number;
  hotel_per_night?: {
    min: number;
    max: number;
    note?: string;
  };
  food_per_day?: {
    min: number;
    max: number;
    note?: string;
  };
  transport_total?: {
    min: number;
    max: number;
    note?: string;
  };
  activities_total?: {
    min: number;
    max: number;
    note?: string;
  };
  total_budget?: {
    min: number;
    max: number;
    note?: string;
  };
  disclaimer?: string;
  currency?: string;
  raw?: string;
}

export interface Hotel {
  name: string;
  description?: string;
  price_per_night?: number;
  rating?: number;
  link: string;
  search_query?: string;
}

export interface Flight {
  origin: string;
  destination: string;
  price: number;
  airline: string;
  link: string;
  depart?: string;
  search_query?: string;
}

export interface Bookings {
  hotels: Hotel[];
  flights: Flight[];
}

export interface MapLocation {
  lat: number;
  lng: number;
}

export interface MapAttraction {
  name: string;
  type: string;
  location: MapLocation;
  wiki?: string;
}

export interface WeatherForecast {
  current: {
    temp_c: number;
    temp_f: number;
    condition: {
      text: string;
      icon: string;
    };
    humidity: number;
    wind_kph: number;
  };
  forecast: {
    date: string;
    maxtemp_c: number;
    maxtemp_f: number;
    mintemp_c: number;
    mintemp_f: number;
    condition: {
      text: string;
      icon: string;
    };
    chance_of_rain: number;
  }[];
}

export interface NewsArticle {
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: string;
  imageUrl?: string;
}

export interface TripResponse {
  itinerary: Itinerary;
  budget: Budget;
  bookings: Bookings;
  mapData: MapAttraction[];
  weather?: WeatherForecast | null;
  news?: NewsArticle[];
}
