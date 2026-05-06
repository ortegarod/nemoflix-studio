import { useState, useEffect, useCallback } from "react";
import type { MediaItem } from "./types";

export default function App() {
  const [items, setItems] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/listing");
      const data = await res.json();
      setItems(data.images || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Nemoflix AMD Gallery</h1>
        <span className="text-sm text-gray-500">{items.length} items</span>
      </header>

      <main className="p-6">
        {loading && items.length === 0 ? (
          <p className="text-gray-500">Loading...</p>
        ) : items.length === 0 ? (
          <p className="text-gray-500">No media yet.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {items.map((item) => (
              <div
                key={item.name}
                onClick={() => setSelected(item.url)}
                className="cursor-pointer rounded-lg overflow-hidden border border-gray-800 hover:border-rose-600 transition aspect-video bg-gray-900 relative group"
              >
                {item.type === "video" ? (
                  <video
                    src={item.url}
                    className="w-full h-full object-cover"
                    preload="metadata"
                    muted
                  />
                ) : (
                  <img
                    src={item.url}
                    alt={item.name}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 opacity-0 group-hover:opacity-100 transition">
                  <p className="text-xs truncate">{item.name}</p>
                </div>
                {item.type === "video" && (
                  <div className="absolute top-2 right-2 bg-black/60 text-white text-[10px] px-1.5 py-0.5 rounded">
                    VIDEO
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      {selected && (
        <div
          className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div className="max-w-full max-h-full" onClick={(e) => e.stopPropagation()}>
            {selected.endsWith(".mp4") || selected.endsWith(".webm") ? (
              <video src={selected} controls autoPlay className="max-w-full max-h-[90vh] rounded" />
            ) : (
              <img src={selected} alt="" className="max-w-full max-h-[90vh] rounded" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
