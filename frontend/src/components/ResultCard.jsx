/**
 * ResultCard
 * ----------
 * Displays the successfully extracted receipt data (vendor, date, total)
 * styled like a printed paper receipt, plus the raw JSON the backend
 * returned (handy for developers integrating the API).
 *
 * Props:
 *   data: { success: true, vendor, date, total }
 */
export default function ResultCard({ data }) {
  const rows = [
    { label: "VENDOR", value: data.vendor },
    { label: "DATE", value: data.date },
    { label: "TOTAL", value: data.total },
  ];

  return (
    <div className="mx-auto w-full max-w-sm">
      {/* Printed-receipt look: paper color, mono font, torn bottom edge */}
      <div className="paper-texture torn-edge rounded-t-lg bg-paper px-6 pt-6 pb-8 shadow-receipt font-mono text-ink">
        <div className="mb-4 border-b border-dashed border-slate-300 pb-4 text-center">
          <p className="text-xs tracking-[0.2em] text-slate-400">
            RECEIPT EXTRACTOR
          </p>
          <p className="mt-1 text-lg font-semibold">Extraction Result</p>
        </div>

        <div className="space-y-3">
          {rows.map((row) => (
            <div key={row.label} className="flex items-start justify-between gap-4">
              <span className="text-xs tracking-wide text-slate-400">
                {row.label}
              </span>
              <span className="text-right font-semibold break-words">
                {row.value}
              </span>
            </div>
          ))}
        </div>

        <div className="mt-6 border-t border-dashed border-slate-300 pt-4 text-center text-[11px] text-slate-400">
          Extracted 100% offline &middot; Tesseract OCR
        </div>
      </div>

      {/* Raw JSON, for developers who want to see the exact API response */}
      <details className="mt-4 rounded-xl border border-slate-200 bg-white open:pb-2">
        <summary className="cursor-pointer select-none px-4 py-3 text-sm font-medium text-slate-500">
          View raw JSON response
        </summary>
        <pre className="mx-4 mb-3 overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs text-emerald-300">
{JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}
