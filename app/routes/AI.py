import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from app import app

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash') 
        print("Pomyślnie skonfigurowano Gemini z modelem 'gemini-2.0-flash'.")
    else:
        model = None
        print("Nie można skonfigurować modelu Gemini - brak klucza API.")
except Exception as e:
    print(f"Błąd podczas konfiguracji Gemini: {e}")
    model = None


def analyze_company_with_gemini(company_name: str) -> dict:
    """
    Analizuje spółkę używając Gemini, zwracając wady, zalety i opinię.
    """
    if not model:
        return {
            "error": "Model Gemini nie jest skonfigurowany. Sprawdź klucz API."
        }

    prompt = f"""
    Jesteś doświadczonym analitykiem finansowym. Twoim zadaniem jest analiza spółki "{company_name}".
    Na podstawie publicznie dostępnych informacji, przedstaw:

    1.  **Zalety inwestowania w spółkę {company_name}:** (wymień w punktach, np. "- Mocna pozycja rynkowa")
    2.  **Wady lub ryzyka związane z inwestowaniem w spółkę {company_name}:** (wymień w punktach, np. "- Duża konkurencja")
    3.  **Opinia inwestorska:** (krótka, 2-3 zdaniowa opinia, czy warto rozważyć inwestycję i dlaczego)

    Odpowiedz zwięźle i konkretnie. Nie dodawaj żadnych wstępów ani podsumowań poza wymaganymi sekcjami.
    Formatuj odpowiedź dokładnie tak, jak poniżej, używając nagłówków "Zalety:", "Wady:", "Opinia inwestorska:".

    Zalety:
    - [Tutaj wypisz zalety]

    Wady:
    - [Tutaj wypisz wady]

    Opinia inwestorska:
    [Tutaj napisz opinię]
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text

        zalety_start = text_response.find("Zalety:")
        wady_start = text_response.find("Wady:")
        opinia_start = text_response.find("Opinia inwestorska:")

        zalety = "Nie znaleziono"
        wady = "Nie znaleziono"
        opinia = "Nie znaleziono"

        if zalety_start != -1 and wady_start != -1:
            zalety = text_response[zalety_start + len("Zalety:"):wady_start].strip()
        elif zalety_start != -1:
             zalety = text_response[zalety_start + len("Zalety:"):].strip()


        if wady_start != -1 and opinia_start != -1:
            wady = text_response[wady_start + len("Wady:"):opinia_start].strip()
        elif wady_start != -1:
            wady = text_response[wady_start + len("Wady:"):].strip()

        if opinia_start != -1:
            opinia = text_response[opinia_start + len("Opinia inwestorska:"):].strip()
        
        zalety_list = [z.strip() for z in zalety.split('\n') if z.strip().startswith("-") or z.strip()]
        wady_list = [w.strip() for w in wady.split('\n') if w.strip().startswith("-") or w.strip()]


        return {
            "spolka": company_name,
            "zalety": zalety_list if zalety_list else zalety,
            "wady": wady_list if wady_list else wady,
            "opinia_inwestorska": opinia,
            "surowa_odpowiedz_bota": text_response
        }
    except Exception as e:
        print(f"Błąd podczas komunikacji z API Gemini: {e}")
        return {
            "error": f"Błąd API Gemini: {str(e)}"
        }

@app.route('/api/analiza_spolki', methods=['GET'])
def endpoint_analiza_spolki():
    company_name = request.args.get('nazwa_spolki')

    if not company_name:
        return jsonify({"blad": "Nie podano parametru 'nazwa_spolki'"}), 400
    
    if not model:
         return jsonify({"blad": "Model Gemini nie jest poprawnie skonfigurowany. Sprawdź logi serwera i klucz API."}), 500


    wynik_analizy = analyze_company_with_gemini(company_name)

    if "error" in wynik_analizy:
        return jsonify(wynik_analizy), 500
    if "blad" in wynik_analizy:
        return jsonify(wynik_analizy), 503


    return jsonify(wynik_analizy)