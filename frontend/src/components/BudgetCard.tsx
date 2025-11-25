'use client';

import { Budget } from '@/types';

interface BudgetCardProps {
  budget: Budget | null;
}

export default function BudgetCard({ budget }: BudgetCardProps) {
  if (!budget) return null;
  if (budget.raw) {
    return (
      <pre className="whitespace-pre-wrap bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mb-5">
        {budget.raw}
      </pre>
    );
  }

  const estimation: any = (budget as any).budget_estimation || budget;

  return (
    <div className="mb-5">
      <h3 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        Budget Estimate
      </h3>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-sm">
        {estimation.city && estimation.days && (
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            <strong>{estimation.city}</strong> • {estimation.days} days
          </div>
        )}

        <div className="grid gap-3">
          {estimation.hotel_per_night && (
            <div className="bg-green-50 dark:bg-green-900/20 p-3.5 rounded-lg border border-green-400">
              <div className="text-sm font-bold text-green-800 dark:text-green-300 mb-1.5">
                Hotel (per night)
              </div>
              <div className="text-lg font-bold text-green-700 dark:text-green-400">
                {estimation.currency || '$'}
                {estimation.hotel_per_night.min} - {estimation.currency || '$'}
                {estimation.hotel_per_night.max}
              </div>
              {estimation.hotel_per_night.note && (
                <div className="text-xs text-green-800 dark:text-green-300 mt-1">
                  {estimation.hotel_per_night.note}
                </div>
              )}
            </div>
          )}

          {estimation.food_per_day && (
            <div className="bg-amber-50 dark:bg-amber-900/20 p-3.5 rounded-lg border border-amber-400">
              <div className="text-sm font-bold text-amber-900 dark:text-amber-300 mb-1.5">
                Food (per day)
              </div>
              <div className="text-lg font-bold text-amber-800 dark:text-amber-400">
                {estimation.currency || '$'}
                {estimation.food_per_day.min} - {estimation.currency || '$'}
                {estimation.food_per_day.max}
              </div>
              {estimation.food_per_day.note && (
                <div className="text-xs text-amber-900 dark:text-amber-300 mt-1">
                  {estimation.food_per_day.note}
                </div>
              )}
            </div>
          )}

          {estimation.transport_total && (
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3.5 rounded-lg border border-blue-400">
              <div className="text-sm font-bold text-blue-900 dark:text-blue-300 mb-1.5">
                Transport (total)
              </div>
              <div className="text-lg font-bold text-blue-800 dark:text-blue-400">
                {estimation.currency || '$'}
                {estimation.transport_total.min} - {estimation.currency || '$'}
                {estimation.transport_total.max}
              </div>
              {estimation.transport_total.note && (
                <div className="text-xs text-blue-900 dark:text-blue-300 mt-1">
                  {estimation.transport_total.note}
                </div>
              )}
            </div>
          )}

          {estimation.activities_total && (
            <div className="bg-pink-50 dark:bg-pink-900/20 p-3.5 rounded-lg border border-pink-500">
              <div className="text-sm font-bold text-pink-900 dark:text-pink-300 mb-1.5">
                Activities (total)
              </div>
              <div className="text-lg font-bold text-pink-800 dark:text-pink-400">
                {estimation.currency || '$'}
                {estimation.activities_total.min} - {estimation.currency || '$'}
                {estimation.activities_total.max}
              </div>
              {estimation.activities_total.note && (
                <div className="text-xs text-pink-900 dark:text-pink-300 mt-1">
                  {estimation.activities_total.note}
                </div>
              )}
            </div>
          )}
        </div>

        {estimation.total_budget && (
          <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-xl border-2 border-purple-400 dark:border-purple-500">
            <div className="text-sm font-bold text-purple-900 dark:text-purple-300 mb-2">
              Total Trip Budget
            </div>
            <div className="text-2xl font-bold text-purple-800 dark:text-purple-400">
              {estimation.currency || '$'}
              {estimation.total_budget.min.toLocaleString()} - {estimation.currency || '$'}
              {estimation.total_budget.max.toLocaleString()}
            </div>
            {estimation.total_budget.note && (
              <div className="text-xs text-purple-900 dark:text-purple-300 mt-2">
                {estimation.total_budget.note}
              </div>
            )}
          </div>
        )}

        {(budget as any).disclaimer && (
          <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs text-gray-600 dark:text-gray-400 italic">
            {(budget as any).disclaimer}
          </div>
        )}
      </div>
    </div>
  );
}
