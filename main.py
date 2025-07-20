from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import pdfplumber
import io

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> Dict[str, float]:
    sum_total = 0.0

    contents = await file.read()
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                headers = table[0]
                try:
                    total_index = headers.index("Total")
                    for row in table[1:]:
                        if row and "Thingamajig" in row[0]:
                            value = row[total_index].replace("$", "").replace(",", "").strip()
                            sum_total += float(value)
                except ValueError:
                    continue  # Skip if headers don't include "Total"

    return {"sum": round(sum_total, 2)}
