/**
 * ImagePreview
 * ------------
 * Shows a thumbnail preview of the selected receipt image, plus its
 * filename/size, before the user clicks "Extract Details".
 *
 * Props:
 *   previewUrl: an object URL (from URL.createObjectURL) pointing to the file.
 *   file: the original File object (used to display name/size).
 *   onClear: callback to remove the current selection.
 */
export default function ImagePreview({ previewUrl, file, onClear }) {
  if (!previewUrl) return null;

  const sizeInKb = file ? Math.round(file.size / 1024) : null;

  return (
    <div className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4">
      <img
        src={previewUrl}
        alt="Receipt preview"
        className="h-24 w-24 rounded-xl object-cover border border-slate-200"
      />
      <div className="flex-1 min-w-0">
        <p className="truncate font-medium text-slate-700">{file?.name}</p>
        {sizeInKb !== null && (
          <p className="text-sm text-slate-400">{sizeInKb} KB</p>
        )}
      </div>
      <button
        type="button"
        onClick={onClear}
        className="shrink-0 rounded-full px-3 py-1.5 text-sm font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
      >
        Remove
      </button>
    </div>
  );
}
