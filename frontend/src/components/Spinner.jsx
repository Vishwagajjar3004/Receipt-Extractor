/**
 * Spinner
 * -------
 * Simple animated loading indicator shown while the backend is
 * processing an uploaded receipt (OCR can take a second or two).
 */
export default function Spinner({ label = "Processing receipt..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10">
      <div
        className="h-10 w-10 rounded-full border-4 border-slate-200 border-t-brand-indigo animate-spin"
        role="status"
        aria-label="Loading"
      />
      <p className="text-sm font-medium text-slate-500">{label}</p>
    </div>
  );
}
