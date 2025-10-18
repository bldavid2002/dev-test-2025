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

#GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME =  "gemini-2.5-pro"

#if not GEMINI_API_KEY:
#    print("Warning: Gemini api key enviroment variable is not set")

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
        
            else:
                text += page.get_text() or ""
        
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
    

def constructSystemPrompt(jsonSchema: str) -> str:
    return f"""
        You are an expert food data extractor, your task is to analyze raw text extracted from a food product document these can be Hungarian, or contain OCR errors you will also need to extract specific nutritional and allergen information
        GOAL: identify the product name 10 specific allergens and 6 specific nutritional values
        ALLERGENS: use boolean values true or false based on the text, if the product is explicitly marked "free" of an allergen, set the value to false if a cross-contamination warning is present set the value to true
        NUTRITIONAL VALUES: extract the value as a string including the correct units example: '1553 kJ' or '376 kcal', '36 g' if a value is not found leave it as null or None
        OUTPUT FORMAT: You MUST strictly adhere to the provided JSON schema, do not include any text, headers, or markdown outside of the final, single JSON object
        JSON SCHEMA:{jsonSchema}
        """

async def callGeminiApi(rawText: str) -> Dict[str, Any]:

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code = 500,
            detail = "LLM Api key not configured"
        )


    try:
       
        genai.configure(api_key = GEMINI_API_KEY)

        schemaJson = ExtractionResult.model_json_schema(by_alias = True)
        logger.info(f"Pydantic schema type: {type(schemaJson).__name__}")
        if isinstance(schemaJson, dict):
            schemaDict = schemaJson
        elif isinstance(schemaJson, str):
            schemaDict = json.loads(schemaJson)
        else:
            raise TypeError(f"Unexpected schema type returned by Pydantic: {type(schemaJson).__name__}")
        
        
        
        generation_config = types.GenerationConfig()

        

        systemPrompt = constructSystemPrompt(schemaJson)

        model = genai.GenerativeModel(
            model_name=MODEL_NAME, 
            system_instruction=systemPrompt
        )

        response = await model.generate_content_async(
            contents = [rawText],
            generation_config = generation_config,
        )

        logger.info(f"Raw LLM response type: {type(response.text).__name__}")
        response_preview = str(response.text)[:500] 
        logger.debug(f"Raw LLM response text: {response_preview}...")

        if isinstance(response.text, dict):
            return response.text
        
        elif isinstance(response.text, str) and response.text.strip():
            try:
                jsonString = response.text.strip()
                if jsonString.startswith("```json"):
                    jsonString = jsonString[7:]
                if jsonString.endswith("```"):
                    jsonString = jsonString[:-3]
                
                jsonString = jsonString.strip()


                return json.loads(jsonString)
            except json.JSONDecodeError as e:

                print(f"LLM returned malformed JSON: {e}, raw response: {response.text}")
                raise Exception(f"LLM returned invalid JSON: {response.text}")
        
        else:
            raise Exception(f"LLM returned empty or unexpected content type: {type(response.text).__name__}")
        

    except GoogleAPICallError as e:
        errorMessage = str(e)
        print(f"Gemini Api Error: {errorMessage}")
        raise HTTPException(
            status_code = 502,
            detail = f"Error communicating with the LLM api: {errorMessage} "
        )
    except Exception as e:
        errorMessage = str(e)
        print(f"General LLM procesing error: {errorMessage}")
        raise HTTPException(

            status_code = 500,
            detail = f"Unexpected error during LLM processing: {str(e)}"
        )

async def extractDataCore(fileStream: io.BytesIO) -> ExtractionResult:
    rawText = process_pdf(fileStream)
    llmJsonData = await callGeminiApi(rawText)
    try:
        validateResult = ExtractionResult(**llmJsonData)
        return validateResult
    except Exception as e:
        print(f"!!! Pydantic Validation Error: {e} !!!")
        raise HTTPException(
            status_code = 422,
            detail = f"LLM otput faild Pydantic validation: {str(e)} raw output: {llmJsonData}"
        )