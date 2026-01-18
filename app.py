import streamlit as st
import requests

# Konfiguracja strony
st.set_page_config(page_title="Allegro Szperacz", page_icon="🛒")
st.title("🛒 Allegro Szperacz")

# --- POBIERANIE SEKRETÓW ---
try:
    CLIENT_ID = st.secrets["allegro"]["client_id"]
    CLIENT_SECRET = st.secrets["allegro"]["client_secret"]
except Exception:
    st.error("Brak kluczy API w 'Secrets'!")
    st.stop()

# --- FUNKCJE ---
def get_token():
    url = "https://allegro.pl/auth/oauth/token"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        r = requests.post(
            url, 
            auth=(CLIENT_ID, CLIENT_SECRET), 
            data={'grant_type': 'client_credentials'},
            headers=headers
        )
        r.raise_for_status()
        return r.json()['access_token']
    except Exception as e:
        st.error(f"Błąd logowania: {e}")
        return None

def search_allegro(token, phrase):
    url = "https://api.allegro.pl/offers/listing"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.allegro.public.v1+json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://allegro.pl/',
        'Origin': 'https://allegro.pl'
    }
    
    params = {
        'phrase': phrase,
        'sort': '+price',
        'limit': 1,
        'sellingMode.format': 'BUY_NOW'
    }
    
    try:
        r = requests.get(url, headers=headers, params=params)
        
        if r.status_code == 403:
            st.error("🔒 Allegro (WAF) zablokowało to zapytanie. Spróbuj za chwilę.")
            return None
            
        r.raise_for_status()
        data = r.json()
        
        items = data.get('items', {}).get('regular', []) + data.get('items', {}).get('promoted', [])
        return items[0] if items else None

    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return None

# --- GUI ---
phrase = st.text_input("Co chcesz znaleźć?", placeholder="np. Lego 42115")

if st.button("🔍 Znajdź najtańszą ofertę", type="primary"):
    if not phrase:
        st.warning("Wpisz nazwę!")
    else:
        with st.spinner('Szukam na Allegro...'):
            token = get_token()
            if token:
                offer = search_allegro(token, phrase)
                
                if offer:
                    price = offer['sellingMode']['price']['amount']
                    currency = offer['sellingMode']['price']['currency']
                    name = offer['name']
                    img = offer['images'][0]['url'] if offer.get('images') else None
                    
                    st.success("Sukces!")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if img: st.image(img)
                    with col2:
                        st.metric("Cena", f"{price} {currency}")
                        st.write(f"**{name}**")
                        st.caption("Oferta 'Kup Teraz'")
                else:
                    st.info("Nic nie znaleziono (lub blokada).")
