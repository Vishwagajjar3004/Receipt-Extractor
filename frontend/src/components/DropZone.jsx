import { useCallback, useRef, useState } from "react";

const ACCEPTED_TYPES = ["image/jpeg", "image/jpg", "image/png"];

/**
 * DropZone
 * --------
 * A drag-and-drop + click-to-browse area for selecting a receipt image.
 *
 * Props:
 *   onFileSelected(file): called with the chosen File object once a
 *                         valid image file is dropped or picked.
 *   onInvalidFile(message): called when the user drops/selects a file
 *                          that isn't jpg/jpeg/png.
 */
export default function DropZone({ onFileSelected, onInvalidFile }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const inputRef = useRef(null);

  const validateAndEmit = useCallback(
    (file) => {
      if (!file) return;
      if (!ACCEPTED_TYPES.includes(file.type)) {
        onInvalidFile?.("Only JPG, JPEG, or PNG images are supported.");
        return;
      }
      onFileSelected(file);
    },
    [onFileSelected, onInvalidFile]
  );

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragActive(false);
    const file = event.dataTransfer.files?.[0];
    validateAndEmit(file);
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];
    validateAndEmit(file);
    // Reset the input value so selecting the same file again still fires onChange.
    event.target.value = "";
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragActive(true);
      }}
      onDragLeave={() => setIsDragActive(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
      }}
      className={`flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed
        px-6 py-14 text-center cursor-pointer transition-colors
        ${
          isDragActive
            ? "border-brand-indigo bg-indigo-50"
            : "border-slate-300 bg-white hover:border-brand-cyan hover:bg-cyan-50/40"
        }`}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-brand-indigo to-brand-cyan text-white text-2xl">
        📄
      </div>
      <div>
        <p className="font-semibold text-slate-700">
          Drag & drop your receipt here
        </p>
        <p className="mt-1 text-sm text-slate-400">
          or click to browse &middot; JPG, JPEG, PNG
        </p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        onChange={handleInputChange}
        className="hidden"
      />
    </div>
  );
}
