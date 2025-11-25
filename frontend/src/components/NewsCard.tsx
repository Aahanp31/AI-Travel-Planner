'use client';

import { NewsArticle } from '@/types';
import { NewspaperIcon } from '@heroicons/react/24/outline';

interface NewsCardProps {
  news?: NewsArticle[];
  destination: string;
}

export default function NewsCard({ news, destination }: NewsCardProps) {
  if (!news || news.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-6 border border-border-subtle shadow-lg">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <NewspaperIcon className="w-5 h-5 text-primary-foreground" />
          </div>
          <h3 className="text-xl font-bold text-card-foreground">Latest News</h3>
        </div>
        <p className="text-muted-foreground text-sm">
          No recent news available for {destination}
        </p>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-6 border border-border-subtle shadow-lg">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
          <NewspaperIcon className="w-5 h-5 text-primary-foreground" />
        </div>
        <h3 className="text-xl font-bold text-card-foreground">Latest News</h3>
      </div>

      <div className="space-y-3">
        {news.map((article, index) => (
          <a
            key={index}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group block p-4 rounded-xl border border-border-subtle bg-gradient-to-r from-muted/30 to-transparent hover:from-primary/10 hover:border-primary transition-all"
          >
            <div className="flex gap-4">
              {article.imageUrl && (
                <div className="flex-shrink-0">
                  <img
                    src={article.imageUrl}
                    alt={article.title}
                    className="w-24 h-24 object-cover rounded-lg"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
              )}

              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-card-foreground mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                  {article.title}
                </h4>

                {article.description && (
                  <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                    {article.description}
                  </p>
                )}

                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="font-medium">{article.source}</span>
                  {article.publishedAt && (
                    <>
                      <span>•</span>
                      <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>

      <div className="mt-5 pt-4 border-t border-border-subtle text-xs text-muted-foreground flex items-center gap-2">
        <NewspaperIcon className="w-4 h-4" />
        Powered by NewsData.io
      </div>
    </div>
  );
}
