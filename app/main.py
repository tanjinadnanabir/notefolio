from fastapi import FastAPI

app = FastAPI(
    title="NoteFolio API",
    description="A free and open-source note-taking API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Notefolio API",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }