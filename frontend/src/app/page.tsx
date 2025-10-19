"use client"
import React, {use, useState, type ChangeEvent, type FC} from 'react';
import type { ExtractionResult, Status } from '@/types';
import { AllergensDisplay, NutritionalValuesDisplay } from '@/components/DataDisplay';
import { Upload, Loader2 } from '@/components/Icons';

const API_BASE_URL = "http://127.0.0.1:8000"

const App: FC = () => {
  const [selectedFile, setSelectedFile] = useState<File|null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [result, setResult] = useState<ExtractionResult|null>(null);
  const [error, setError] = useState<string|null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files ? event.target.files[0] : null;

      if (file && file.type !== "application/pdf"){
        setError("Rossz file típus. Kérlek PDF file-t tölts fel") 
        setSelectedFile(null);
        setResult(null);;
        setStatus('error');
        return
      }


      setSelectedFile(file);
      setError(null)

      if (status === 'success' || status === 'error') {
        setStatus('idle');
        setResult(null);
      }
  };



  const handleUpload = async () => {
  if(!selectedFile){
    setError("Kérlek válasz egy PDF filet");
    setStatus('error');
    return;
  }

  setStatus('loading');
  setError(null);
  setResult(null);

  const formData = new FormData();
  formData.append('file', selectedFile);

  try{
    const response = await fetch(`${API_BASE_URL}/extract/`,{
      method: 'POST',
      body: formData,

    });

    const data = await response.json();

    if(!response.ok) {
      const errorMessage = data.detail || `HTTP Error ${response.status}: Faild to process file.`;
    }

    setResult(data as ExtractionResult);
    setStatus('success');

  }catch(err: unknown) {
    console.error ("Upload Failed",err);
    let message = "Could not connect to back end API"
    if(err instanceof Error){
      message = err.message
    }
    
    setError(`Extraction Faild: ${message}`);
    setStatus('error');
  }
};
const isButtonDisabled = (status === 'loading' || !selectedFile);
const isError  = (status === 'error');
const isSuccess = (status === 'success');

return(
    <div className='font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 bg-gray-900 text-white'>
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-4xl">
        <h1 className="text-4xl font-extrabold tracking-tight text-center sm:text-5xl text-blue-400">
          Tápanyag és Allergén elemző
        </h1>
        <p className="text-lg text-gray-400 text-center max-w-2xl">
          Tölts fel egy PDF dokumentumot, majd olvass egy összefoglalót a tápanyagokról és tartalmazott allergénekről.
        </p>
        <div className="w-full bg-gray-800 rounded-2xl p-6 shadow-2xl border border-gray-700">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            
            <label className="flex flex-col items-center justify-center p-4 w-full sm:w-1/2 border-2 border-dashed rounded-lg cursor-pointer bg-gray-700/50 border-gray-600 hover:border-blue-400 transition-all">
              <Upload size={24} className="text-blue-400" />
              <span className="mt-2 text-sm text-gray-300">
                {selectedFile ? selectedFile.name : 'Click to select a PDF file'}
              </span>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
            <button
              onClick={handleUpload}
              disabled={isButtonDisabled}
              className={`w-full sm:w-auto h-12 px-10 rounded-full font-semibold transition-colors flex items-center justify-center gap-2 
                ${isButtonDisabled
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-500/30'
                }`}
            >
              {status === 'loading' && <Loader2 size={20} className="animate-spin" />}
              {status === 'loading' ? 'Dokumentum feldolgozása folyamatban' : 'Feldolgozás'}
            </button>
          </div>
          <div className="mt-4 text-center">
            {isError && (
              <div className="text-red-400 font-medium p-2 bg-red-900/30 rounded-lg border border-red-800">
                {error}
              </div>
            )}
            {isSuccess && (
              <div className="text-green-400 font-medium p-2 bg-green-900/30 rounded-lg border border-green-800">
                Sikeres feldolgozás! Az adatokat alul olvashatod.
              </div>
            )}
            {status === 'idle' && selectedFile && (
              <div className="text-gray-400 p-2">Keszen áll az adat feldolgozásra <strong>{selectedFile.name}</strong>.</div>
            )}
          </div>
        </div>
        {result && (
          <div className="w-full mt-6 space-y-6">
            <div className="bg-gray-800 rounded-xl p-4 shadow-2xl border border-blue-600/50">
              <h2 className="text-2xl font-bold mb-2 text-blue-300">{result.productName}</h2>
              <p className="text-sm text-gray-400">Language Detected: <span className="font-semibold text-gray-200">{result.language}</span></p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AllergensDisplay allergens={result.allergens} />
              <NutritionalValuesDisplay nutritionalValues={result.nutritionalValues} />
            </div>
          </div>
        )}
      </main>
    </div>

)
};

export default App;

