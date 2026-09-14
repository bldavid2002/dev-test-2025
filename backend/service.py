import os
import io
import json
from typing import Dict, Any, Union
from fastapi import HTTPException
from pydantic import BaseModel
from pypdf import PdfReader, errors as pdf_errors
import google.generativeai as genai
from google.generativeai import types
from google.api_core.exceptions import GoogleAPICallError
from models import ExtractionResult
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


MODEL_NAME =  "gemini-3.6-flash"


logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO)

def extractTextFromPdf(fileStream: io.BytesIO) -> str:
    try:
        fileStream.seek(0)
        reader = PdfReader(fileStream)
        text = ""
        for page in reader.pages:
            pageText = page.extract_text() 
        
            if  pageText:
                text += pageText or ""
        
        if not text.strip() or len(text.strip()) < 50:
            raise ValueError("Minimal or no text extractable")

        return text
    
    except pdf_errors.PdfReadError:
        raise ValueError("The uploded file is not a valid PDF or corrupted")
    finally:
        fileStream.seek(0)


def extractTextWithOCR(fileStream: io.BytesIO) -> str:
    ocrText = ""
    try:
        fileStream.seek(0)
        pdfBytes = fileStream.read()

        pages = convert_from_bytes(pdfBytes)

        for i, pageImage in enumerate(pages):
            pageText = pytesseract.image_to_string(pageImage, lang='eng+hun')
            ocrText += pageText + f"\n Page {i+1} End \n"
        
        if not ocrText.strip():
            raise HTTPException(
                status_code=400,
                detail = "OCR failed to find meaningful text"
            )
        
        print("successfully extracted text from OCR")
        return ocrText
    
    except Exception as e:
        if "No such file in the directory" in str(e) or "poppler" in str(e).lower():
            raise HTTPException(
                status_code = 501,
                detail=(
                    "OCR failed: poppler",
                    "was not found. you must install the poppler command line utility"
                    "on your OS and add its 'bin' folder to your systems's Path "
                )
            )
    finally:
        fileStream.seek(0)

    
def process_pdf(fileStream: io.BytesIO) -> str:
    try:
        raw_text = extractTextFromPdf(fileStream)
        return raw_text
    except ValueError as e:
        print(f"Error : {e}. attempting ocr")
        return extractTextWithOCR(fileStream)
    



async def extractDataCore(fileStream: io.BytesIO) -> ExtractionResult:
    rawText = process_pdf(fileStream)
    #llmJsonData = await callGeminiApi(rawText)

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code = 500,
            detail = "LLM Api key not configured"
        )
    
    try:
     #   validateResult = ExtractionResult(**llmJsonData)
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = textSplitter.split_text(rawText)
        docs = [Document(page_content=chunk) for chunk in chunks]
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorStore = Chroma.from_documents(documents=docs, embedding=embeddings)
        retriever = vectorStore.as_retriever(search_kwargs={"k": 6})
        query = "Extract the product name, 10 allergens, and 6 nutritional values from the text."
        relevant_docs = retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0, google_api_key=GEMINI_API_KEY)
        structured_llm = llm.with_structured_output(ExtractionResult)

        prompt = (
            f"You are an expert food data extractor. Analyze the following text extracted from a product PDF.\n"
            f"GOAL: Output strictly according to the schema. Include 10 specific allergens (true/false) "
            f"and 6 specific nutritional values (with units like '1553 kJ' or '36 g').\n"
            f"ALLERGEN RULES: If explicitly marked 'free', set to false. If cross-contamination warning is present, set to true.\n\n"
            f"Context:\n{context}"
        )

        result = await structured_llm.ainvoke(prompt)
        return result
    except Exception as e:
        logger.error(f"LangChain Extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document using RAG: {str(e)}"
        )