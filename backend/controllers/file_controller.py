# Autor: Brooklyn Muñoz

from pathlib import Path

from app import App
from models.file_response import FileResponse

app = App.get_instance().app


@app.get("/files/info")
def read_info_file() -> FileResponse:
    file_path = Path(__file__).parents[1] / "data" / "info.txt"

    with open(file_path, "r", encoding = "utf-8") as file:
        content = file.read()

    return FileResponse(content)
