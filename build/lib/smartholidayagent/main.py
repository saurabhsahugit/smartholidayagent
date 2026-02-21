from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SmartHolidayAgent")
app.mount("/static", StaticFiles(directory="src/smartholidayagent/static"), name="static")