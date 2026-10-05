/**
 * ErrorCard
 * ---------
 * Displays a clear error message when extraction fails — either because
 * the image isn't a valid receipt, the file was invalid, or the request
 * failed for some other reason.
 *
 * Props:
 *   message: string describing what went wrong.
 */
export default function ErrorCard({ message }) {
  return (
    <div className="mx-auto flex w-full max-w-sm items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50 p-5">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-rose-100 text-rose-500">
        ⚠
      </div>
      <div>
        <p className="font-semibold text-rose-700">Extraction failed</p>
        <p className="mt-1 text-sm text-rose-600">{message}</p>
      </div>
    </div>
  );
}
