import streamlit as st
import requests
import base64

# Tytuł strony
st.set_page_config(page_title="Allegro Szperacz", page_icon="🛒")
st.title("🛒 Allegro Szperacz")

# --- POBIERANIE SEKRETÓW (BEZPIECZNE) ---
# Klucze nie są wpisane tutaj, tylko w panelu Streamlit!
try:
    CLIENT_ID = st.secrets["allegro"]["client_id"]
    CLIENT_SECRET = st.secrets["allegro"]["client_secret"]
except Exception:
    st.error("Brak skonfigurowanych kluczy API!")
    st.stop()

# --- FUNKCJE ---
def get_token():
    url = "https://allegro.pl/auth/oauth/token"
    try:
        r = requests.post(
            url, 
            auth=(CLIENT_ID, CLIENT_SECRET), 
            data={'grant_type': 'client_credentials'}
        )
        r.raise_for_status()
        return r.json()['access_token']
    except Exception as e:
        st.error(f"Błąd logowania do Allegro: {e}")
        return None

def search_allegro(token, phrase):
    url = "https://api.allegro.pl/offers/listing"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.allegro.public.v1+json',
        # Streamlit działa na serwerze, więc udajemy przeglądarkę
        'User-Agent': 'Mozilla/5.0 (compatible; MyAllegroApp/1.0)'
    }
    params = {
        'phrase': phrase,
        'sort': '+price',
        'limit': 1,
        'sellingMode.format': 'BUY_NOW'
    }
    
    try:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        items = data.get('items', {}).get('regular', []) + data.get('items', {}).get('promoted', [])
        
        if items:
            return items[0]
        else:
            return None
    except Exception as e:
        st.error(f"Błąd szukania: {e}")
        return None

# --- INTERFEJS ---
product_name = st.text_input("Co chcesz znaleźć?", placeholder="np. iPhone 13")

if st.button("🔍 Znajdź najtańszą ofertę", type="primary"):
    if not product_name:
        st.warning("Wpisz nazwę produktu!")
    else:
        with st.spinner('Łączę z Allegro...'):
            token = get_token()
            if token:
                offer = search_allegro(token, product_name)
                
                if offer:
                    price = offer['sellingMode']['price']['amount']
                    currency = offer['sellingMode']['price']['currency']
                    name = offer['name']
                    img = offer['images'][0]['url'] if offer.get('images') else None
                    
                    st.success("Znaleziono!")
                    st.metric(label="Najniższa cena", value=f"{price} {currency}")
                    st.write(f"**Produkt:** {name}")
                    if img:
                        st.image(img, width=200)
                else:
                    st.info("Nie znaleziono ofert 'Kup Teraz'.")

# Stopka
st.markdown("---")
st.caption("Aplikacja edukacyjna korzystająca z Allegro API")