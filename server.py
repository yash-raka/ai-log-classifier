# 1. IMPORT TORCH FIRST (This prevents the WinError 1114 DLL crash)
import torch

# 2. Import everything else
import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse

# CHANGED: Import classify_log instead of classify_csv
from classify import classify_log 
import uvicorn

app = FastAPI()

@app.post("/classify/")
async def classify_logs(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")
    
    try:
        # Read the uploaded file into a dataframe
        df = pd.read_csv(file.file)
        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'log_message' columns.")

        # CHANGED: Run classify_log on each row individually
        df["target_label"] = [
            classify_log(src, msg) 
            for src, msg in zip(df["source"], df["log_message"])
        ]

        print("Dataframe classified successfully.")

        output_file = "resources/output.csv"
        df.to_csv(output_file, index=False)
        print(f"File saved to {output_file}")
        
        return FileResponse(output_file, media_type='text/csv', filename="output.csv")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

# 3. RUN SERVER DIRECTLY IN MAIN THREAD
if __name__ == "__main__":
    print("Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)