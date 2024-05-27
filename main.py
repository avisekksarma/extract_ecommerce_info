from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, field_validator
from bs4 import BeautifulSoup
import base64
from extractor.extractor import Extractor


app = FastAPI()

class HTMLInput(BaseModel):
    html_block : str
    prompt: str = ""
    model: str = "llama3:8b"

    @field_validator("model")
    def validate_model(cls, v):
        valid_models = ["llama3:8b", "llama3:70b", "phi3:mini", "phi3:medium", "mistral", "gemma:2b", "gemma:7b"]
        if v not in valid_models:
            raise ValueError(f"Invalid model choice. Must be one of: {', '.join(valid_models)}")
        return v


# validity checks
def is_html_block(html_block:str) -> bool :
    soup = BeautifulSoup(html_block, 'lxml')
    # checks if passed string has at least one html tag, if so the parser will make into valid html block
    has_valid_html_tag = bool(soup.find())
    return has_valid_html_tag

# api routes: 

@app.get('/api/health')
async def root():
    return {"success":True, "status_code":200, "message":"The web app is working correctly."}

@app.post('/api/send_html_encoded')
async def send_html(data:HTMLInput):
    """
    Since we need to manually escape all the quotation marks while serializing the html block when passing as an input in api
    which becomes cumbersome, otherwise serialization fails,
    so here the Input html block is passed as base64 encoded from client side.
    """
    coded_string = data.html_block
    decoded_bytes = base64.b64decode(coded_string)
    html_block = decoded_bytes.decode('utf-8')
    if not html_block:
        raise HTTPException(status_code=400,detail="HTML block is not passed in request body")
    if not is_html_block(html_block):
        raise HTTPException(status_code=400,detail="Passed content is not HTML content.")
    extractor_obj = Extractor(model=data.model, prompt_content=data.prompt)
    answer = extractor_obj.query_ollama(html_block)
    return {"success":True,"status_code":200, "extracted_data":answer}
