export interface NavigatorItem {
  number: string;
  label: string;
  path: string;
  available: boolean;
}

export const NAVIGATOR_ITEMS: NavigatorItem[] = [
  { number: "01", label: "Library", path: "/library", available: true },
  { number: "02", label: "Project Overview", path: "/overview", available: false },
  { number: "03", label: "Book Settings", path: "/settings/book", available: false },
  { number: "04", label: "Canon & Visual DNA", path: "/canon", available: false },
  { number: "05", label: "Manuscript", path: "/manuscript", available: false },
  { number: "06", label: "Page Planner", path: "/planner", available: false },
  { number: "07", label: "Interior Studio", path: "/interior", available: false },
  { number: "08", label: "Cover Studio", path: "/cover", available: false },
  { number: "09", label: "Book Gallery", path: "/gallery", available: false },
  { number: "10", label: "Review & Validation", path: "/review", available: false },
  { number: "11", label: "Export & Reports", path: "/export", available: false },
  { number: "12", label: "GCU Engine", path: "/gcu", available: false },
  { number: "13", label: "Backup & Storage", path: "/backup", available: false },
  { number: "14", label: "Settings", path: "/settings", available: true },
];
