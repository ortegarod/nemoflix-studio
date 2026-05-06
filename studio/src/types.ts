export interface MediaItem {
  name: string;
  type: "image" | "video";
  width: number;
  height: number;
  mtime: number;
  url: string;
}
