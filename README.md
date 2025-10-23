# Allergén és Tápérték Elemző PDF-ből

Webalkalmazás, amely mesterséges intelligencia (LLM) segítségével automatikusan kinyeri az élelmiszertermékek allergénjeit és tápérték jellemzőit a feltöltött PDF dokumentumokból.



## Felhasználói Dokumentáció



### A program célja

Az alkalmazás célja, hogy strukturálatlan  PDF termékleírásokból kinyerje a legfontosabb allergén (például: glutén, tej, szója) és tápérték (pl. energia, zsír, fehérje) adatokat, és azokat, strukturált formában jelenítse meg a felhasználó számára.

### Használat lépései

1.  Nyisd meg az alkalmazást a böngésződben.
2.  Kattints a "Click to select a PDF file" a fájl kiválasztásához.
3.  Válassz ki egy `.pdf` kiterjesztésű fájlt a számítógépedről.
4.  A fájl kiválasztása után kattints a "Feldolgozás" gombra.
5.  Várj, amíg a rendszer feldolgozza a dokumentumot. 
6.  A sikeres feldolgozás után az oldalon megjelennek a kinyert adatok:
    * A termék neve és a felismert nyelv.
    * **Allergének:** Lista a keresett allergénekről, jelezve, hogy a termék tartalmazza-e megfelelő címkével ellátva.
    * **Tápanyagok:** Táblázat a kinyert tápanyagokról és azok mennyiségéről.

---

## Fejlesztői Dokumentáció


### Felhasznált Technológiák

* **Frontend:** React (Next.js), TypeScript, Tailwind CSS
* **Backend:** Python 3.14, FastAPI
* **AI / Adatkinyerés:** Google Gemini (Modell: gemini-1.5-pro)
* **PDF Feldolgozás:**
    * `pypdf`: Szöveges PDF-ek olvasása.
    * `pdf2image` és `pytesseract`: Szkennelt  PDF-ek OCR.
* **Adatmodellezés:** Pydantic
* **Szerver:** Uvicorn

### Előkövetelmények

A projekt futtatásához az alábbi eszközök telepítése szükséges:

1.  **Node.js** 
2.  **Python** 
3.  **Poppler:** A `pdf2image` külső függősége. Ezt az operációs rendszerednek megfelelően kell telepíteni.
4.  **Tesseract OCR:** A `pytesseract` külső függősége.

### Telepítés és Futtatás (Lokálisan)

A projekt két fő részből áll: `backend` és `frontend`. Mindkettőt külön terminálban kell futtatni.

### Megjegyzés a Render Szolgáltatásról

**A Render-en telepített ingyenes (Free Tier) szolgáltatás a production ready verzió bemutatásához, alacsony memóriakorláttal rendelkezik. A szkennelt PDF-ek (OCR) feldolgozása rendkívül memóriaigényes.**

**Emiatt a Render szolgáltatás nagyobb, szkennelt fájlok feldolgozásakor leállhat (Out-of-Memory hiba).**

**Megbízható működéshez, különösen nagy vagy szkennelt PDF-ek esetén, az alkalmazás lokális (localhost) futtatása ajánlott az alábbi lépések szerint.**

#### 1. Backend (FastAPI)

```bash
# 1. Lépj be a backend mappába
cd backend

# 2. Hozz létre egy virtuális környezetet
python -m venv venv

# 3. Aktiváld a virtuális környezetet
venv\Scripts\activate


# 4. Telepítsd a Python függőségeket
pip install -r requirements.txt

# 5. Hozz létre egy .env fájlt a backend mappában
# A .env fájl tartalma:
GEMINI_API_KEY="ITT_ADD_MEG_A_GEMINI_API_KULCSODAT"

# 6. Indítsd el a FastAPI szervert
uvicorn main:app --reload
```
A backend most már fut a `http://127.0.0.1:8000` címen.

#### 2. Frontend (React/Next.js)

```bash
# 1. Lépj be a frontend mappába (egy ÚJ terminálban)
cd frontend

# 2. Telepítsd a Node.js függőségeket
npm install

# 3. Indítsd el a fejlesztői szervert
npm run dev
```
Az alkalmazás most már elérhető a `http://localhost:3000` címen.

### API Végpont

Az alkalmazás egyetlen fő API végpontot használ:

#### `POST /extract/`

* **Leírás:** Feldolgoz egy feltöltött PDF fájlt és visszaadja a kinyert adatokat.
* **Request Body:** `multipart/form-data`
    * `file`: A feltöltendő PDF fájl.
* **Sikeres Válasz (200):** `ExtractionResult` JSON objektum.

* **Hiba Válaszok:**
    * `400 (Bad Request)`: Például nem PDF fájl lett feltöltve.
    * `500 (Internal Server Error)`: Általános szerverhiba  LLM API hiba.
    * `501 (Not Implemented)`: Ha az OCR-hez szükséges Poppler nincs telepítve.