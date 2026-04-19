import uvicorn
import os
import sys

if __name__ == "__main__":
    # Definimos las carpetas que contienen nuestro código fuente
    # para evitar que uvicorn vigile .venv o archivos temporales
    source_dirs = ["adapters", "agent", "core", "di"]
    
    # Verificamos que las carpetas existan antes de pasarlas a uvicorn
    existing_dirs = [d for d in source_dirs if os.path.isdir(d)]
    
    print(f"Iniciando servidor de desarrollo...")
    print(f"Vigilando cambios en: {existing_dirs} y main.py")
    print("============================ \n")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=existing_dirs,
        reload_includes=["main.py", ".env"]
    )
