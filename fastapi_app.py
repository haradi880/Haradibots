from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from main import Chatbot

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize chatbot
chatbot = Chatbot()
chatbot.train()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("message", "").strip()
    
    if not user_input:
        return {"response": "Please enter a message"}
    
    intent = chatbot.classify_intent(user_input)
    response = chatbot.get_response(intent, user_input)
    
    return {
        "response": response,
        "intent": intent,
        "emotion": chatbot.current_emotion
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)