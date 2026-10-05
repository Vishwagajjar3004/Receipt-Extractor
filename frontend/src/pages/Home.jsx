import { useState } from "react";
import axios from "axios";
import DropZone from "../components/DropZone.jsx";
import ImagePreview from "../components/ImagePreview.jsx";
import Spinner from "../components/Spinner.jsx";
import ResultCard from "../components/ResultCard.jsx";
import ErrorCard from "../components/ErrorCard.jsx";

// Base URL of the FastAPI backend. Override via a .env file
// (VITE_API_BASE_URL=...) if the backend runs somewhere other than
// localhost:8000.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null); // successful extraction data
  const [errorMessage, setErrorMessage] = useState(null);

  /** Store the selected file and generate a preview URL for it. */
  const handleFileSelected = (selectedFile) => {
    setErrorMessage(null);
    setResult(null);
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
  };

  /** Reset everything back to the initial empty state. */
  const handleReset = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMessage(null);
    setIsLoading(false);
  };

  /** Send the selected file to the backend's /extract endpoint. */
  const handleUpload = async () => {
    if (!file) return;

    setIsLoading(true);
    setErrorMessage(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/extract`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data?.success) {
        setResult(response.data);
      } else {
        setErrorMessage(response.data?.message || "Receipt not detected.");
      }
    } catch (error) {
      // Network errors, backend 500s, etc. all land here.
      const backendMessage = error.response?.data?.message;
      setErrorMessage(
        backendMessage ||
          "Could not reach the server. Please check that the backend is running."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto flex min-h-screen max-w-2xl flex-col px-4 py-10">
        {/* Header */}
        <header className="mb-8 text-center">
          <div className="mx-auto mb-3 inline-flex items-center gap-2 rounded-full bg-white px-4 py-1.5 text-xs font-medium text-slate-500 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            100% offline &middot; No cloud AI
          </div>
          <h1 className="text-3xl font-bold text-slate-800 sm:text-4xl">
            Image{" "}
            <span className="bg-gradient-to-r from-brand-indigo to-brand-cyan bg-clip-text text-transparent">
              Information 
            </span>
          </h1>
          <p className="mt-2 text-slate-500">
            Upload an image — get the vendor, date, and total back as JSON.
          </p>
        </header>

        {/* Main card */}
        <main className="flex-1 space-y-5">
          {!previewUrl && (
            <DropZone
              onFileSelected={handleFileSelected}
              onInvalidFile={(msg) => setErrorMessage(msg)}
            />
          )}

          {previewUrl && !result && (
            <ImagePreview previewUrl={previewUrl} file={file} onClear={handleReset} />
          )}

          {previewUrl && !isLoading && !result && (
            <div className="flex justify-center gap-3">
              <button
                type="button"
                onClick={handleUpload}
                className="rounded-xl bg-gradient-to-r from-brand-indigo to-brand-cyan px-6 py-3 font-semibold text-white shadow-lg shadow-indigo-200 transition-transform hover:scale-[1.02] active:scale-[0.98]"
              >
                Extract Details
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="rounded-xl border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-600 hover:bg-slate-50"
              >
                Reset
              </button>
            </div>
          )}

          {isLoading && <Spinner />}

          {!isLoading && result && (
            <>
              <ResultCard data={result} />
              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={handleReset}
                  className="mt-2 rounded-xl border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Extract Another Receipt
                </button>
              </div>
            </>
          )}

          {!isLoading && errorMessage && (
            <>
              <ErrorCard message={errorMessage} />
              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={handleReset}
                  className="mt-2 rounded-xl border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Try Again
                </button>
              </div>
            </>
          )}
        </main>

        <footer className="mt-10 text-center text-xs text-slate-400">
          Built with FastAPI, Tesseract OCR & React &middot; RemoteDevs Infoteach
        </footer>
      </div>
    </div>
  );
}
