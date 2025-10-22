import logging
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import ExtractionResult
from service import extractTextFromPdf, extractDataCore

load_dotenv()

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title = "Allergén kiválasztó")
VERCEL_APP_URL = "https://dev-test-2025-lqdy.vercel.app"
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    VERCEL_APP_URL,
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/")
async def root():
    return{"message":"PDF analizáló fut"}

@app.post("/extract/", response_model = ExtractionResult)
async def extractDataFromPdf(
    file: UploadFile = File(..., description = "The food product specificaton PDF to analyze")
):
    logger.info(f"Recived file: {file.filename}")
    if file.content_type not in ["application/pdf"]:
        raise HTTPException(status_code = 400, detail = "Only PDF are accepted")
    
    fileData = await file.read()
    try:
        fileStream = io.BytesIO(fileData)
        extractionResult = await extractDataCore(fileStream)
        return JSONResponse(
            status_code = 200,
            content = extractionResult.model_dump() 
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Final extraction failed with an unhandled error: {e}")
        raise HTTPException(status_code = 500, detail = "unknonw error occured durin processing")