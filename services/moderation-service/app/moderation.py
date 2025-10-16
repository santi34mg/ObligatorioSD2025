from typing import List

PROHIBITED_WORDS = ["spam", "insulto", "violencia"]

def check_profanity(text: str) -> List[str]:
    #Detecta palabras prohibidas simples
    found = [w for w in PROHIBITED_WORDS if w.lower() in text.lower()]
    return found

def check_length(text: str) -> bool:
    #Revisa si el texto es demasiado corto o largo
    return 10 <= len(text) <= 10000

def moderate_text(text: str):
    #Evalúa el texto y devuelve estado general
    banned = check_profanity(text)
    length_ok = check_length(text)
    if banned:
        return {"status": "rejected", "reason": f"Palabras prohibidas: {', '.join(banned)}"}
    if not length_ok:
        return {"status": "rejected", "reason": "Longitud no permitida"}
    return {"status": "approved", "reason": "Contenido aceptado"}
