#!/usr/bin/env python3
"""Build the Dentist Pro static site.

Generates index.html, locations/*.html, thank-you.html, 404.html and sitemap.xml
from the data below so the header, footer, NAP details and schema stay identical
on every page. The generated HTML is committed, so hosting needs no build step.

    python3 scripts/build.py

Edit SITE / TREATMENTS / LOCATIONS here, then re-run.
"""

import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Clinic details  (replace every "[...]" placeholder — see README)
# --------------------------------------------------------------------------
SITE = {
    "name": "Dentist Pro",
    "tagline": "Dental Clinic · Iloilo City",
    "domain": "https://www.dentistpro-iloilo.com",  # [YOUR DOMAIN]
    "phone_display": "0993 495 3526",
    "phone_tel": "+639934953526",
    "email": "[YOUR-EMAIL]@gmail.com",  # [YOUR EMAIL]
    "facebook": "https://www.facebook.com/",  # [YOUR FACEBOOK PAGE URL]
    "street": "Nabitasan",
    "district": "La Paz",
    "city": "Iloilo City",
    "region": "Iloilo",
    "postal": "5000",
    "country": "PH",
    "lat": 10.7134,  # [VERIFY] drop a pin on your clinic in Google Maps
    "lng": 122.5653,
    # [CONFIRM HOURS]
    "hours": [
        ("Monday – Friday", "9:00 AM – 6:00 PM", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "09:00", "18:00"),
        ("Saturday", "9:00 AM – 5:00 PM", ["Saturday"], "09:00", "17:00"),
        ("Sunday", "By appointment", [], None, None),
    ],
    "formspree": "https://formspree.io/f/YOUR_FORM_ID",  # [YOUR FORMSPREE ID]
}
SITE["address_line"] = f'{SITE["street"]}, {SITE["district"]}, {SITE["city"]}'
SITE["address_full"] = f'{SITE["address_line"]}, {SITE["region"]} {SITE["postal"]}, Philippines'
MAP_QUERY = quote_plus(f'{SITE["street"]}, {SITE["district"]}, {SITE["city"]}')
MAP_EMBED = f"https://maps.google.com/maps?q={MAP_QUERY}&z=15&output=embed"
MAP_LINK = f"https://www.google.com/maps/search/?api=1&query={MAP_QUERY}"

# --------------------------------------------------------------------------
# Icons (inline SVG, stroke-based)
# --------------------------------------------------------------------------
_I = {
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 13 17 22l-5-3-5 3 1.5-9"/>',
    "tooth": '<path d="M12 3c-2 0-3 1-5 1S4 3 3 4.5C2 6 2.3 8.6 3 11c.7 2.6 1 5.3 1.8 8.2.3 1.4 1 2.8 2 2.8 1.4 0 1.5-2.3 2.2-4.8.4-1.5 1.1-2.6 3-2.6s2.6 1.1 3 2.6c.7 2.5.8 4.8 2.2 4.8 1 0 1.7-1.4 2-2.8.8-2.9 1.1-5.6 1.8-8.2.7-2.4 1-5 0-6.5C20 3 18 4 17 4s-3-1-5-1z"/>',
    "sparkle": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>',
    "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
    "drill": '<path d="M14 4h6v6h-6z"/><path d="M14 7H6l-3 3 3 3h8"/><path d="M9 13v7"/>',
    "braces": '<rect x="2" y="8" width="20" height="8" rx="4"/><path d="M7 8v8M12 8v8M17 8v8M2 12h20"/>',
    "implant": '<path d="M7 3h10l-1 6H8z"/><path d="M9 9h6M9.5 12h5M10 15h4M10.5 18h3M12 18v3"/>',
    "child": '<circle cx="12" cy="6" r="3"/><path d="M12 9v6M8 21l4-6 4 6M6 12h12"/>',
    "extract": '<path d="M8 2v6l-3 3M16 2v6l3 3"/><path d="M12 13c-3 0-4 2-4 4s1 5 2 5 1-2 2-2 1 2 2 2 2-3 2-5-1-4-4-4z"/>',
    "root": '<path d="M12 2c-4 0-6 2-6 5 0 4 2 6 3 10 .5 2 1 5 2 5h2c1 0 1.5-3 2-5 1-4 3-6 3-10 0-3-2-5-6-5z"/><path d="M12 7v12"/>',
    "denture": '<path d="M3 10c0-3 4-6 9-6s9 3 9 6v2H3z"/><path d="M6 12v3M10 12v4M14 12v4M18 12v3M3 12c0 5 4 8 9 8s9-3 9-8"/>',
    "veneer": '<path d="M6 4h12v6c0 6-3 10-6 10s-6-4-6-10z"/><path d="M9 7h6"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    "nav": '<path d="m3 11 19-9-9 19-2-8z"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_I[name]}</svg>')


# --------------------------------------------------------------------------
# Content data
# --------------------------------------------------------------------------
TREATMENTS = [
    ("Check-up & Teeth Cleaning", "tooth", "Oral prophylaxis, scaling and a full check-up to keep teeth and gums healthy. Looking for teeth cleaning near me? Start here."),
    ("Tooth Fillings", "drill", "Tooth-coloured composite fillings that repair cavities and chipped teeth while looking natural."),
    ("Root Canal Treatment", "root", "Save an infected or badly decayed tooth and stop the pain instead of having it pulled."),
    ("Tooth Extraction", "extract", "Gentle simple and surgical extractions, including impacted wisdom teeth (odontectomy)."),
    ("Braces & Orthodontics", "braces", "Metal, ceramic and self-ligating braces plus retainers to straighten teeth and fix your bite."),
    ("Teeth Whitening", "sparkle", "Professional in-clinic and take-home whitening for a brighter smile, safely."),
    ("Veneers", "veneer", "Thin composite or porcelain shells that reshape and brighten front teeth."),
    ("Dentures", "denture", "Complete and partial dentures — including flexible dentures — to restore your smile and chewing."),
    ("Crowns, Bridges & Implants", "implant", "Replace missing or broken teeth with fixed crowns, bridges or dental implants."),
    ("Pediatric Dentistry", "child", "Kid-friendly check-ups, fluoride and sealants. A patient pediatric dentist near me for your little ones."),
]

CONCERNS = [
    ("🦷", "Toothache or swelling", "Throbbing pain, swelling or a tooth that hurts when you bite.", "Root Canal Treatment", "Check-up, filling or root canal"),
    ("🩸", "Bleeding or swollen gums", "Gums that bleed when brushing can be an early sign of gum disease.", "Check-up & Teeth Cleaning", "Deep cleaning & gum care"),
    ("😬", "Crooked or gapped teeth", "Crowding, gaps, overbite or underbite affecting your confidence.", "Braces & Orthodontics", "Braces or veneers"),
    ("☕", "Yellow or stained teeth", "Coffee, tea and smoking stains that brushing won't remove.", "Teeth Whitening", "Cleaning & whitening"),
    ("🕳️", "Missing teeth", "Gaps that make chewing hard or make you hide your smile.", "Crowns, Bridges & Implants", "Dentures, bridge or implant"),
    ("🧊", "Sensitive teeth", "Sharp twinges with cold drinks, sweets or brushing.", "Tooth Fillings", "Desensitizing or fillings"),
    ("😮‍💨", "Bad breath", "Persistent bad breath despite brushing and mouthwash.", "Check-up & Teeth Cleaning", "Cleaning & oral exam"),
    ("😰", "Dental anxiety", "Nervous about the dentist? We go slow and explain every step.", "Check-up & Teeth Cleaning", "Gentle, no-pressure visit"),
]

HOME_FAQS = [
    ("Where is the nearest dentist near me in Iloilo City?",
     f"{SITE['name']} is located at {SITE['address_line']}. We are a short ride from Jaro, Lapuz, Mandurriao, "
     "City Proper and Molo, and we welcome patients from all over Metro Iloilo. Tap \"Get Directions\" on this page for the fastest route."),
    ("Do you accept walk-in patients?",
     f"Yes, walk-ins are welcome when a slot is available, but booking ahead guarantees your time. Call or text {SITE['phone_display']} "
     "or use the appointment form and we'll confirm your schedule."),
    ("Is there a dentist near me open on Saturday in Iloilo?",
     "Yes. Dentist Pro is open on Saturdays, and Sunday visits are available by appointment — ideal if you work or study on weekdays."),
    ("Do you handle dental emergencies?",
     "If you need an emergency dentist near me for severe toothache, swelling, a broken tooth or a knocked-out tooth, call us right away. "
     "We prioritise urgent cases and will advise you on what to do before you arrive."),
    ("How much does teeth cleaning or braces cost in Iloilo City?",
     "Prices depend on your needs, so we give you a clear quote after your check-up — no surprise fees. Message us for current rates and "
     "ask about installment options for braces, dentures and other larger treatments."),
    ("Do you accept HMO?",
     "We accept selected HMO and dental plans. Contact us with your HMO name so we can confirm your coverage before your visit."),
]

# Areas served — Iloilo City districts and nearby high-population Metro Iloilo towns.
LOCATIONS = [
    {
        "slug": "la-paz", "name": "La Paz", "kind": "district",
        "distance": "right here in La Paz", "time": "a few minutes",
        "landmarks": ["La Paz Public Market", "La Paz Plaza", "Huervana Street", "Nabitasan"],
        "intro": [
            "Looking for a dentist near me in La Paz? Dentist Pro is right in your neighbourhood, in Barangay Nabitasan. "
            "Whether you live near La Paz Plaza, shop at the La Paz Public Market or commute along Huervana Street, quality dental care is only minutes away.",
            "Because we're local, it's easy to drop by for a quick cleaning before work, bring the kids after school, or come in "
            "the same day when a toothache can't wait.",
        ],
        "route": "From La Paz Plaza or the public market, it's a short tricycle or jeepney ride to Nabitasan. Tell the driver \"Nabitasan, La Paz\" — "
                 "or tap Get Directions below and Google Maps will guide you door to door.",
        "faqs": [
            ("Is Dentist Pro the closest dentist to La Paz Public Market?",
             "We're a short ride from the La Paz Public Market and plaza, so it's easy to fit a check-up into your errands."),
            ("Can I walk in if I live in La Paz?",
             f"Yes — La Paz residents can walk in when a slot is open. Text {SITE['phone_display']} first to skip the wait."),
        ],
        "near": ["jaro", "lapuz", "city-proper", "mandurriao"],
    },
    {
        "slug": "jaro", "name": "Jaro", "kind": "district",
        "distance": "about 2–4 km", "time": "10–15 minutes",
        "landmarks": ["Jaro Metropolitan Cathedral", "Jaro Plaza & Belfry", "Central Philippine University", "E. Lopez Street"],
        "intro": [
            "Searching for a dentist near me in Jaro? Dentist Pro in neighbouring La Paz is one of the closest dental clinics to Jaro — "
            "just a short trip from the Jaro Cathedral, Jaro Plaza and Central Philippine University.",
            "Jaro is home to many families and students, so we offer flexible schedules, kid-friendly care and braces for teens "
            "and young professionals who want a straighter smile.",
        ],
        "route": "From Jaro Plaza, head toward La Paz and ask for Nabitasan. Jeepneys passing through La Paz and tricycles from Jaro "
                 "can bring you close to the clinic. Travel time is usually 10–15 minutes, depending on traffic.",
        "faqs": [
            ("Is there a dentist near Central Philippine University?",
             "Yes. Dentist Pro is a short ride from CPU and the Jaro area, making it convenient for students and staff between classes."),
            ("Do you offer braces for students from Jaro?",
             "We do. Ask about our braces options and flexible monthly payment plans during your consultation."),
        ],
        "near": ["la-paz", "lapuz", "mandurriao", "pavia", "leganes"],
    },
    {
        "slug": "mandurriao", "name": "Mandurriao", "kind": "district",
        "distance": "about 4–6 km", "time": "15–20 minutes",
        "landmarks": ["SM City Iloilo", "Iloilo Business Park", "Smallville", "Atria Park District"],
        "intro": [
            "Need a dentist near me in Mandurriao? Dentist Pro serves patients from Iloilo Business Park, Smallville, SM City Iloilo "
            "and the growing residential villages around Benigno Aquino Avenue (Diversion Road).",
            "Many of our Mandurriao patients are BPO and office workers, so we keep evening-friendly weekday hours and Saturday "
            "appointments to fit around your shift.",
        ],
        "route": "From SM City Iloilo or Iloilo Business Park, take Benigno Aquino Avenue (Diversion Road) toward La Paz, then head to Nabitasan. "
                 "By car or Grab it's typically 15–20 minutes.",
        "faqs": [
            ("Are you near Iloilo Business Park and SM City?",
             "Yes. We're about 15–20 minutes by car from Iloilo Business Park and SM City Iloilo via Diversion Road."),
            ("Can BPO employees book after work or on Saturdays?",
             "Absolutely — message us your preferred time and we'll do our best to fit around your shift, including Saturdays."),
        ],
        "near": ["la-paz", "jaro", "molo", "city-proper"],
    },
    {
        "slug": "molo", "name": "Molo", "kind": "district",
        "distance": "about 5–6 km", "time": "15–25 minutes",
        "landmarks": ["Molo Church (St. Anne Parish)", "Molo Plaza", "Molo Mansion"],
        "intro": [
            "If you're looking for a dentist near me in Molo, Dentist Pro welcomes patients from around Molo Plaza, the historic Molo Church "
            "and the Molo Mansion area.",
            "From routine teeth cleaning to dentures for lolo and lola, we care for the whole family under one roof.",
        ],
        "route": "From Molo Plaza, ride a jeepney toward the City Proper and connect to a La Paz route, or take a taxi or Grab straight to Nabitasan, La Paz "
                 "— usually 15–25 minutes.",
        "faqs": [
            ("Do you make dentures for senior patients from Molo?",
             "Yes. We make complete, partial and flexible dentures and take extra care with senior patients' comfort and fit."),
            ("How long is the trip from Molo to your clinic?",
             "Usually 15–25 minutes by car, depending on traffic through the City Proper."),
        ],
        "near": ["arevalo", "mandurriao", "city-proper", "oton"],
    },
    {
        "slug": "arevalo", "name": "Arevalo", "kind": "district",
        "distance": "about 8–10 km", "time": "25–35 minutes",
        "landmarks": ["Villa Beach", "Arevalo Plaza", "Santo Niño de Arevalo Church"],
        "intro": [
            "Residents of Villa Arevalo searching for a dentist near me can count on Dentist Pro for complete, family-friendly dental care.",
            "We help Arevalo patients make the most of each trip — book your check-up, cleaning and any follow-up treatment in as few visits as possible.",
        ],
        "route": "From Arevalo Plaza or Villa Beach, travel through Molo toward the City Proper and on to La Paz. "
                 "By car it's typically 25–35 minutes; tap Get Directions for live traffic.",
        "faqs": [
            ("Can I finish my treatment in fewer visits since I live in Arevalo?",
             "Tell us when you book. Where it's safe, we combine procedures to reduce the number of trips you need to make."),
            ("Do you treat children from Arevalo?",
             "Yes — we see kids for check-ups, fluoride, sealants and gentle extractions of baby teeth."),
        ],
        "near": ["molo", "oton", "mandurriao", "city-proper"],
    },
    {
        "slug": "city-proper", "name": "City Proper", "kind": "district",
        "distance": "about 3–4 km", "time": "10–20 minutes",
        "landmarks": ["Calle Real (J.M. Basa Street)", "Plaza Libertad", "Iloilo City Hall", "Iloilo Provincial Capitol"],
        "intro": [
            "Working or studying downtown and need a dentist near me in Iloilo City Proper? Dentist Pro is a quick hop from Calle Real, "
            "Plaza Libertad and the government offices around City Hall and the Provincial Capitol.",
            "Squeeze in a lunch-break consultation or a quick cleaning — we respect your time and keep appointments on schedule.",
        ],
        "route": "From Calle Real or Plaza Libertad, take a La Paz-bound jeepney or a short taxi/Grab ride across the river to Nabitasan. "
                 "Usually 10–20 minutes.",
        "faqs": [
            ("Can I visit during my lunch break from downtown?",
             "Yes. Book ahead and choose a late-morning or early-afternoon slot — a basic check-up or cleaning usually fits in an hour."),
            ("Which jeepney goes from the City Proper to La Paz?",
             "La Paz-bound jeepneys from downtown pass near our area. Ask the driver for Nabitasan, or message us and we'll guide you."),
        ],
        "near": ["la-paz", "lapuz", "molo", "mandurriao"],
    },
    {
        "slug": "lapuz", "name": "Lapuz", "kind": "district",
        "distance": "about 2–4 km", "time": "10–15 minutes",
        "landmarks": ["Iloilo Commercial Port Complex (Loboc)", "Lapuz Public Market area", "Lapuz Norte & Sur"],
        "intro": [
            "Lapuz, once part of La Paz, is our next-door neighbour — so if you're searching for a dentist near me in Lapuz, "
            "Dentist Pro is one of the nearest clinics you'll find.",
            "We see many port and industrial workers from Lapuz. If you need a quick fix for a broken tooth or toothache, call us and we'll fit you in.",
        ],
        "route": "From Lapuz, head toward La Paz and ask for Barangay Nabitasan. A tricycle or short Grab ride typically takes 10–15 minutes.",
        "faqs": [
            ("Is your clinic close to Lapuz?",
             "Yes. Lapuz borders La Paz, so most patients reach us in 10–15 minutes."),
            ("Do you accept same-day toothache cases from Lapuz?",
             f"Yes, whenever we can. Call {SITE['phone_display']} as early as possible so we can prepare a slot for you."),
        ],
        "near": ["la-paz", "jaro", "city-proper"],
    },
    {
        "slug": "pavia", "name": "Pavia", "kind": "town",
        "distance": "about 6–9 km", "time": "20–30 minutes",
        "landmarks": ["Pavia Town Plaza", "Santa Monica Parish Church", "Ungka area", "Iloilo–Capiz Road"],
        "intro": [
            "Pavia is one of Metro Iloilo's fastest-growing towns, and many families there search for a trusted dentist near me in Iloilo City. "
            "Dentist Pro is an easy drive from the Pavia plaza, the Ungka area and the subdivisions along the Iloilo–Capiz Road.",
            "Skip the long queues — book online and arrive at your scheduled time.",
        ],
        "route": "From Pavia, travel south along the Iloilo–Capiz Road through Ungka and Jaro, then continue to La Paz and Nabitasan. "
                 "Expect about 20–30 minutes by car, depending on traffic.",
        "faqs": [
            ("How far is Dentist Pro from Pavia?",
             "Roughly 6–9 km — about 20–30 minutes by car via Jaro."),
            ("Do Pavia patients need an appointment?",
             "Walk-ins are welcome, but since you're travelling, we recommend booking so your slot is ready when you arrive."),
        ],
        "near": ["jaro", "santa-barbara", "leganes", "la-paz"],
    },
    {
        "slug": "oton", "name": "Oton", "kind": "town",
        "distance": "about 12–14 km", "time": "30–45 minutes",
        "landmarks": ["Oton Town Plaza", "Oton Church", "Iloilo–Antique Road"],
        "intro": [
            "Oton, one of the oldest towns in Iloilo, is home to many families commuting into the city every day. If you're in Oton and "
            "searching for a dentist near me, Dentist Pro offers complete dental services in one trip to the city.",
            "We'll plan your visits around your commute and combine treatments where we safely can.",
        ],
        "route": "From Oton, take the national highway (Iloilo–Antique Road) through Arevalo and Molo, then head to La Paz. "
                 "Allow about 30–45 minutes depending on traffic.",
        "faqs": [
            ("Is it worth travelling from Oton to Dentist Pro?",
             "Many Oton patients combine their dental visit with work or errands in the city. We keep appointments on time so your trip is worth it."),
            ("Can I get braces adjustments scheduled around my Oton commute?",
             "Yes. We'll set a regular adjustment schedule that fits your travel days."),
        ],
        "near": ["arevalo", "molo", "san-miguel"],
    },
    {
        "slug": "leganes", "name": "Leganes", "kind": "town",
        "distance": "about 9–11 km", "time": "25–35 minutes",
        "landmarks": ["Leganes Town Plaza", "Shrine of San Vicente Ferrer", "Leganes coastal road"],
        "intro": [
            "Leganes residents looking for a dentist near me can reach Dentist Pro quickly via Jaro. We care for patients from the "
            "town proper, the area around the Shrine of San Vicente Ferrer and the growing subdivisions along the coastal road.",
            "From kids' first check-ups to replacing missing teeth, we offer complete family dentistry in one convenient clinic.",
        ],
        "route": "From Leganes, travel toward Jaro and continue into La Paz to reach Nabitasan. The trip usually takes 25–35 minutes by car.",
        "faqs": [
            ("How do I get to Dentist Pro from Leganes?",
             "Head south toward Jaro, then on to La Paz. Tap Get Directions on this page for turn-by-turn guidance."),
            ("Do you offer dentures and implants for Leganes patients?",
             "Yes — we offer dentures, bridges and implant options, and we'll explain which is right for your budget and needs."),
        ],
        "near": ["jaro", "pavia", "la-paz"],
    },
    {
        "slug": "santa-barbara", "name": "Santa Barbara", "kind": "town",
        "distance": "about 15–17 km", "time": "35–50 minutes",
        "landmarks": ["Santa Barbara Church & Plaza", "Iloilo Golf & Country Club", "Road to Iloilo International Airport"],
        "intro": [
            "Santa Barbara, the historic town of the 1898 Cry of Santa Barbara, is part of the growing northern corridor of Metro Iloilo. "
            "If you're there searching for a dentist near me, Dentist Pro is a straightforward drive into the city.",
            "We help out-of-town patients plan treatments efficiently, so you spend less time travelling and more time smiling.",
        ],
        "route": "From Santa Barbara, drive toward Pavia and Jaro along the Iloilo–Capiz Road, then continue to La Paz. "
                 "Expect about 35–50 minutes depending on traffic.",
        "faqs": [
            ("Are you near the Iloilo airport road?",
             "We're in La Paz, Iloilo City — about 35–50 minutes from Santa Barbara via Pavia and Jaro, so it's easy to plan a visit around a city trip."),
            ("Can I book a full check-up and cleaning in one visit?",
             "Yes. A check-up and cleaning are usually done in the same appointment."),
        ],
        "near": ["pavia", "jaro", "leganes"],
    },
    {
        "slug": "san-miguel", "name": "San Miguel", "kind": "town",
        "distance": "about 15–17 km", "time": "35–50 minutes",
        "landmarks": ["San Miguel Town Plaza", "San Miguel Church", "Route via Oton"],
        "intro": [
            "San Miguel families searching for a dentist near me in Iloilo can rely on Dentist Pro for gentle, complete dental care in the city.",
            "We'll give you a clear treatment plan and price estimate on your first visit, so you know exactly how many trips you'll need.",
        ],
        "route": "From San Miguel, travel through Oton and continue along the national highway via Arevalo and Molo into the city, then to La Paz. "
                 "Allow about 35–50 minutes.",
        "faqs": [
            ("How long is the trip from San Miguel?",
             "Usually 35–50 minutes by car via Oton and Molo, depending on traffic."),
            ("Will I get a price estimate before treatment?",
             "Yes — we explain your options and costs after the check-up, before any treatment begins."),
        ],
        "near": ["oton", "arevalo", "molo"],
    },
]
LOC_BY_SLUG = {l["slug"]: l for l in LOCATIONS}


def loc_full(l):
    return f'{l["name"]}, Iloilo City' if l["kind"] == "district" else f'{l["name"]}, Iloilo'


# --------------------------------------------------------------------------
# Schema.org JSON-LD
# --------------------------------------------------------------------------
def business_schema(area_served=None):
    hours = []
    for _, _, days, opens, closes in SITE["hours"]:
        if days:
            hours.append({"@type": "OpeningHoursSpecification", "dayOfWeek": days, "opens": opens, "closes": closes})
    if area_served is None:
        area_served = [{"@type": "City", "name": "Iloilo City"}] + [
            {"@type": "Place", "name": loc_full(l)} for l in LOCATIONS
        ]
    return {
        "@context": "https://schema.org",
        "@type": "Dentist",
        "@id": f'{SITE["domain"]}/#dentist',
        "name": SITE["name"],
        "description": "Dental clinic in La Paz, Iloilo City offering check-ups, cleaning, fillings, root canal, extractions, "
                       "braces, whitening, veneers, dentures and implants.",
        "url": f'{SITE["domain"]}/',
        "telephone": SITE["phone_tel"],
        "image": f'{SITE["domain"]}/images/og-image.png',
        "logo": f'{SITE["domain"]}/images/logo.svg',
        "priceRange": "₱₱",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": f'{SITE["street"]}, {SITE["district"]}',
            "addressLocality": SITE["city"],
            "addressRegion": SITE["region"],
            "postalCode": SITE["postal"],
            "addressCountry": SITE["country"],
        },
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["lat"], "longitude": SITE["lng"]},
        "hasMap": MAP_LINK,
        "openingHoursSpecification": hours,
        "areaServed": area_served,
        "sameAs": [SITE["facebook"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Dental Treatments",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "MedicalProcedure", "name": t[0]}} for t in TREATMENTS
            ],
        },
    }


def faq_schema(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs
        ],
    }


def breadcrumb_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)
        ],
    }


def jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'


# --------------------------------------------------------------------------
# Shared page parts
# --------------------------------------------------------------------------
def head(title, desc, path, prefix, schemas=(), robots="index, follow", keywords=""):
    url = f'{SITE["domain"]}/{path}'
    kw = f'\n  <meta name="keywords" content="{escape(keywords)}">' if keywords else ""
    return f'''<!doctype html>
<html lang="en-PH">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">{kw}
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{url}">
  <meta name="geo.region" content="PH-ILI">
  <meta name="geo.placename" content="{SITE["city"]}">
  <meta name="geo.position" content="{SITE["lat"]};{SITE["lng"]}">
  <meta name="ICBM" content="{SITE["lat"]}, {SITE["lng"]}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_PH">
  <meta property="og:site_name" content="{SITE["name"]}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE["domain"]}/images/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(desc)}">
  <meta name="twitter:image" content="{SITE["domain"]}/images/og-image.png">
  <meta name="theme-color" content="#0e7c86">
  <link rel="icon" href="{prefix}images/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{prefix}images/apple-touch-icon.png">
  <link rel="manifest" href="{prefix}site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/styles.css">
  {"".join(jsonld(s) for s in schemas)}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''


def header(prefix, home):
    h = "" if home else f"{prefix}index.html"
    links = [("Treatments", "#treatments"), ("Concerns", "#concerns"), ("Results", "#results"),
             ("Credentials", "#credentials"), ("About Us", "#about"), ("Areas", "#areas"), ("Contact", "#contact")]
    nav = "".join(f'<li><a href="{h}{a}">{n}</a></li>' for n, a in links)
    book = "#book"  # every page has its own booking form
    return f'''<div class="topbar">
  <div class="container">
    <span>📍 {SITE["address_line"]}</span>
    <span>Open Mon–Sat · Call/Text <a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a></span>
  </div>
</div>
<header class="header">
  <div class="container header__inner">
    <a class="logo" href="{prefix}index.html" aria-label="{SITE["name"]} home">
      <img src="{prefix}images/logo.svg" alt="{SITE["name"]} logo" width="38" height="38">
      <span>{SITE["name"]}<small>{SITE["tagline"]}</small></span>
    </a>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">{nav}</ul>
    </nav>
    <div class="header__cta">
      <a class="btn btn--ghost btn--sm" href="tel:{SITE["phone_tel"]}">{icon("phone")}Call {SITE["phone_display"]}</a>
      <a class="btn btn--primary btn--sm" href="{book}">{icon("calendar")}Book Appointment</a>
    </div>
    <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu">{icon("menu")}</button>
  </div>
</header>
<div class="action-bar">
  <a href="tel:{SITE["phone_tel"]}">{icon("phone")}Call Now</a>
  <a href="{book}">{icon("calendar")}Book Now</a>
</div>
'''


def areas_list(prefix, current=None):
    items = []
    for l in LOCATIONS:
        cur = ' aria-current="page"' if l["slug"] == current else ""
        items.append(f'<li><a href="{prefix}locations/{l["slug"]}.html"{cur}>Dentist near {l["name"]}</a></li>')
    return f'<ul class="areas">{"".join(items)}</ul>'


def hours_table():
    rows = "".join(f"<tr><td>{d}</td><td>{t}</td></tr>" for d, t, *_ in SITE["hours"])
    return f'<table class="hours"><tbody>{rows}</tbody></table>'


def footer(prefix):
    tl = "".join(f'<li><a href="{prefix}index.html#treatments">{t[0]}</a></li>' for t in TREATMENTS[:6])
    al = "".join(f'<li><a href="{prefix}locations/{l["slug"]}.html">Dentist near {l["name"]}</a></li>' for l in LOCATIONS[:7])
    al2 = "".join(f'<li><a href="{prefix}locations/{l["slug"]}.html">Dentist near {l["name"]}</a></li>' for l in LOCATIONS[7:])
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div>
        <a class="logo" href="{prefix}index.html"><img src="{prefix}images/logo.svg" alt="" width="38" height="38" loading="lazy"><span>{SITE["name"]}<small>{SITE["tagline"]}</small></span></a>
        <p>Your friendly dentist near me in Iloilo City — gentle, modern and affordable dental care for the whole family.</p>
        <address style="font-style:normal">
          <strong>{SITE["name"]}</strong><br>
          {SITE["street"]}, {SITE["district"]}<br>{SITE["city"]}, {SITE["region"]} {SITE["postal"]}<br>
          <a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a>
        </address>
      </div>
      <div><h3>Treatments</h3><ul>{tl}</ul></div>
      <div><h3>Iloilo City Districts</h3><ul>{al}</ul></div>
      <div><h3>Nearby Towns</h3><ul>{al2}</ul>
        <h3 class="mt-2">Follow Us</h3><ul><li><a href="{SITE["facebook"]}" rel="noopener" target="_blank">Facebook</a></li></ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© <span class="js-year">{date.today().year}</span> {SITE["name"]}, {SITE["city"]}. All rights reserved.</span>
      <span>Dentist near me · Dental clinic in La Paz, Iloilo City, Philippines</span>
    </div>
  </div>
</footer>
<script src="{prefix}js/main.js" defer></script>
</body>
</html>
'''


def booking_section(prefix, location=None):
    area = location["name"] if location else "Iloilo City"
    opts = "".join(f'<option value="{escape(t[0])}">{escape(t[0])}</option>' for t in TREATMENTS)
    hidden_loc = f'<input type="hidden" name="area" value="{escape(loc_full(location))}">' if location else ""
    return f'''<section class="section section--soft" id="book" aria-labelledby="book-title">
  <div class="container booking">
    <div class="booking__info">
      <span class="eyebrow">Book Online</span>
      <h2 id="book-title">Book Your Appointment with a Dentist Near {escape(area)}</h2>
      <p>Fill out the form and we'll call or text you to confirm your schedule — usually within the same day during clinic hours.</p>
      <ul class="checklist">
        <li>No booking fee</li>
        <li>Same-day slots for toothache when available</li>
        <li>Clear quote before any treatment</li>
        <li>Walk-ins welcome, appointments prioritised</li>
      </ul>
      <p><strong>Prefer to call?</strong><br><a class="btn btn--light mt-2" href="tel:{SITE["phone_tel"]}">{icon("phone")}Call / Text {SITE["phone_display"]}</a></p>
    </div>
    <form class="form js-booking" name="appointment" method="POST" action="{SITE["formspree"]}" data-netlify="true" netlify-honeypot="company" novalidate>
      <input type="hidden" name="form-name" value="appointment">
      <input type="hidden" name="_subject" value="New appointment request — {SITE["name"]}">
      {hidden_loc}
      <p class="hp"><label>Company <input name="company" tabindex="-1" autocomplete="off"></label></p>
      <div class="form__row form__row--2">
        <div class="field"><label for="f-name">Full name <span class="req">*</span></label><input id="f-name" name="name" autocomplete="name" required><span class="field__error" aria-live="polite"></span></div>
        <div class="field"><label for="f-phone">Mobile number <span class="req">*</span></label><input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="09XX XXX XXXX" required><span class="field__error" aria-live="polite"></span></div>
      </div>
      <div class="form__row form__row--2">
        <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email"><span class="field__error" aria-live="polite"></span></div>
        <div class="field"><label for="f-service">Treatment <span class="req">*</span></label>
          <select id="f-service" name="service" required><option value="">Select a treatment</option>{opts}<option value="Not sure / Consultation">Not sure — consultation</option></select><span class="field__error" aria-live="polite"></span></div>
      </div>
      <div class="form__row form__row--2">
        <div class="field"><label for="f-date">Preferred date</label><input id="f-date" name="date" type="date"><span class="field__error" aria-live="polite"></span></div>
        <div class="field"><label for="f-time">Preferred time</label>
          <select id="f-time" name="time"><option value="">Any time</option><option>Morning (9 AM – 12 PM)</option><option>Afternoon (1 PM – 4 PM)</option><option>Late afternoon (4 PM – 6 PM)</option></select><span class="field__error" aria-live="polite"></span></div>
      </div>
      <div class="field"><label for="f-msg">Describe your concern</label><textarea id="f-msg" name="message" placeholder="e.g. toothache on lower left side for 3 days"></textarea><span class="field__error" aria-live="polite"></span></div>
      <div class="field field--check"><input id="f-consent" name="consent" type="checkbox" value="yes" required><label for="f-consent">I agree to be contacted by {SITE["name"]} about my appointment. My details are handled in line with the Philippine Data Privacy Act of 2012.</label><span class="field__error" aria-live="polite"></span></div>
      <button class="btn btn--primary" type="submit">Request Appointment</button>
      <div class="form__status" role="status" aria-live="polite"></div>
    </form>
  </div>
</section>
'''


def contact_section(location=None):
    title = (f"Find Our Dental Clinic — Directions from {location['name']}" if location
             else "Find Our Dental Clinic in La Paz, Iloilo City")
    if location:
        dir_url = ("https://www.google.com/maps/dir/?api=1&origin=" + quote_plus(loc_full(location))
                   + "&destination=" + MAP_QUERY)
    else:
        dir_url = "https://www.google.com/maps/dir/?api=1&destination=" + MAP_QUERY
    return f'''<section class="section" id="contact" aria-labelledby="contact-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Location & Hours</span>
      <h2 id="contact-title">{escape(title)}</h2>
      <p>Searching for a dental clinic near me? We're easy to reach from anywhere in Metro Iloilo.</p>
    </div>
    <div class="grid grid--2">
      <div class="map-wrap">
        <iframe src="{MAP_EMBED}" title="Map showing {SITE["name"]} in {SITE["address_line"]}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
      </div>
      <div>
        <ul class="contact-list">
          <li>{icon("pin")}<div><strong>Address</strong>{SITE["address_full"]}</div></li>
          <li>{icon("phone")}<div><strong>Call or text</strong><a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a></div></li>
          <li>{icon("mail")}<div><strong>Email</strong><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></div></li>
          <li>{icon("clock")}<div style="flex:1"><strong>Clinic hours</strong>{hours_table()}</div></li>
        </ul>
        <div class="hero__ctas">
          <a class="btn btn--brand" href="{dir_url}" target="_blank" rel="noopener">{icon("nav")}Get Directions</a>
          <a class="btn btn--ghost" href="tel:{SITE["phone_tel"]}">{icon("phone")}Call Now</a>
        </div>
      </div>
    </div>
  </div>
</section>
'''


def faq_section(faqs, title, prefix_id="faq"):
    items = []
    for i, (q, a) in enumerate(faqs):
        aid = f"{prefix_id}-a{i}"
        items.append(f'''<div class="faq__item">
        <h3 style="margin:0"><button class="faq__q" type="button" aria-expanded="false" aria-controls="{aid}">{escape(q)}</button></h3>
        <div class="faq__a" id="{aid}" hidden><p>{escape(a)}</p></div>
      </div>''')
    return f'''<section class="section" id="faq" aria-labelledby="faq-title">
  <div class="container">
    <div class="section__head"><span class="eyebrow">FAQ</span><h2 id="faq-title">{escape(title)}</h2></div>
    <div class="faq">
      {"".join(items)}
    </div>
  </div>
</section>
'''


def cta_band(text):
    return f'''<section class="cta-band">
  <div class="container">
    <h2>{escape(text)}</h2>
    <p>Call, text or book online — our friendly team in La Paz, Iloilo City is ready to help.</p>
    <div class="hero__ctas">
      <a class="btn btn--primary" href="#book">{icon("calendar")}Book Appointment</a>
      <a class="btn btn--light" href="tel:{SITE["phone_tel"]}">{icon("phone")}{SITE["phone_display"]}</a>
    </div>
  </div>
</section>
'''


def treatment_cards(heading_level="h3"):
    cards = []
    for name, ic, desc in TREATMENTS:
        cards.append(f'''<article class="card">
        <div class="card__icon">{icon(ic)}</div>
        <{heading_level}>{escape(name)}</{heading_level}>
        <p>{escape(desc)}</p>
        <a class="card__link" href="#book" data-service="{escape(name)}">Book {escape(name.split(" &")[0].lower())}</a>
      </article>''')
    return f'<div class="grid grid--3">{"".join(cards)}</div>'


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def page_home():
    title = "Dentist Near Me in Iloilo City | Dentist Pro – La Paz Dental Clinic"
    desc = (f"Looking for a dentist near me in Iloilo City? Dentist Pro in Nabitasan, La Paz offers cleaning, braces, "
            f"root canal, extraction, whitening & dentures. Call {SITE['phone_display']} or book online today.")
    keywords = ("dentist near me, dental clinic near me, dentist Iloilo City, dentist La Paz Iloilo, emergency dentist near me, "
                "braces near me, teeth cleaning near me, tooth extraction near me, pediatric dentist near me, affordable dentist Iloilo")
    schemas = [
        business_schema(),
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": f'{SITE["domain"]}/'},
        faq_schema(HOME_FAQS),
    ]
    concerns = "".join(
        f'''<a class="concern" href="#book" data-service="{escape(svc)}">
        <span class="concern__emoji" aria-hidden="true">{emo}</span>
        <div><h3>{escape(t)}</h3><p>{escape(d)}</p><span class="fix">→ {escape(fix)}</span></div>
      </a>''' for emo, t, d, svc, fix in CONCERNS)

    cases = [
        ("whitening", "Teeth Whitening", "Stained, yellowed teeth brightened with a professional in-clinic whitening session."),
        ("braces", "Braces / Orthodontics", "Crowded, crooked teeth aligned with braces over a personalised treatment plan."),
        ("implant", "Missing Tooth Replacement", "A front-tooth gap restored with a natural-looking fixed replacement."),
    ]
    ba = "".join(f'''<article class="ba">
        <div class="ba__frame">
          <img src="images/case-{k}-before.svg" alt="Before {escape(t.lower())} at Dentist Pro Iloilo City" width="640" height="480" loading="lazy">
          <img class="ba__after" src="images/case-{k}-after.svg" alt="After {escape(t.lower())} at Dentist Pro Iloilo City" width="640" height="480" loading="lazy">
          <input class="ba__range" type="range" min="0" max="100" value="50" aria-label="Drag to compare before and after {escape(t.lower())}">
          <span class="ba__handle" aria-hidden="true"></span>
          <span class="ba__tag ba__tag--before">Before</span><span class="ba__tag ba__tag--after">After</span>
        </div>
        <div class="ba__body"><h3>{escape(t)}</h3><p>{escape(d)}</p></div>
      </article>''' for k, t, d in cases)

    creds = [
        ("award", "PRC-Licensed Dentists", "Every dentist on our team holds a valid Professional Regulation Commission (PRC) license."),
        ("users", "Philippine Dental Association", "Active members of the PDA — Iloilo Chapter, committed to ethical, up-to-date practice."),
        ("shield", "Strict Sterilization", "Autoclave-sterilized instruments, single-use disposables and DOH infection-control protocols."),
        ("sparkle", "Continuing Education", "Regular trainings in orthodontics, endodontics and cosmetic dentistry. [Add your certificates]"),
        ("card", "HMO & Flexible Payment", "Selected HMOs accepted. Cash, GCash and installment options for major treatments. [Confirm list]"),
        ("heart", "Gentle, Patient-First Care", "Clear explanations, transparent pricing and a calm clinic for anxious patients and kids."),
    ]
    cred_html = "".join(f'''<div class="card cred"><div class="card__icon">{icon(i)}</div><div><h3>{t}</h3><p>{escape(d)}</p></div></div>'''
                        for i, t, d in creds)

    testimonials = [
        ("[Patient name], Jaro", "Sample review — replace with a real Google review. Very gentle cleaning and the dentist explained everything clearly."),
        ("[Patient name], Mandurriao", "Sample review — replace with a real Google review. Got my braces here and the monthly adjustments are always on time."),
        ("[Patient name], La Paz", "Sample review — replace with a real Google review. They took my child's toothache case the same day. Highly recommended!"),
    ]
    quotes = "".join(f'''<figure class="quote"><div class="stars" aria-hidden="true">★★★★★</div><blockquote><p>{escape(q)}</p></blockquote><figcaption>— {escape(n)}</figcaption></figure>'''
                     for n, q in testimonials)

    body = f'''<main id="main">
<section class="hero" aria-labelledby="hero-title">
  <div class="container hero__grid">
    <div>
      <span class="eyebrow">Dentist Near Me · La Paz, Iloilo City</span>
      <h1 id="hero-title">Your Trusted Dentist Near Me in Iloilo City</h1>
      <p class="hero__lead">Gentle, modern and affordable dental care at {SITE["name"]} in Nabitasan, La Paz. From teeth cleaning and fillings to braces,
      root canal and dentures — everything your family's smile needs, close to home.</p>
      <div class="hero__ctas">
        <a class="btn btn--primary" href="#book">{icon("calendar")}Book an Appointment</a>
        <a class="btn btn--ghost" href="tel:{SITE["phone_tel"]}">{icon("phone")}Call {SITE["phone_display"]}</a>
      </div>
      <ul class="hero__badges">
        <li>{icon("check")}PRC-licensed dentists</li>
        <li>{icon("check")}Walk-ins & same-day toothache care</li>
        <li>{icon("check")}Open Saturdays</li>
        <li>{icon("check")}HMO & installment options</li>
      </ul>
    </div>
    <div class="hero__art">
      <img src="images/hero.svg" alt="Friendly dentist at Dentist Pro, a dental clinic near me in La Paz, Iloilo City" width="600" height="520" fetchpriority="high">
      <div class="hero__card">{icon("pin")}<span><strong>Nabitasan, La Paz</strong>Minutes from Jaro, Lapuz & City Proper</span></div>
    </div>
  </div>
</section>

<section class="section" id="treatments" aria-labelledby="treatments-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Our Treatments</span>
      <h2 id="treatments-title">Dental Treatments in Iloilo City</h2>
      <p>Complete general, cosmetic and orthodontic dentistry in one clinic — so you never have to search "dentist near me" again.</p>
    </div>
    {treatment_cards()}
  </div>
</section>

<section class="section section--soft" id="concerns" aria-labelledby="concerns-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Common Concerns</span>
      <h2 id="concerns-title">What's Bothering Your Smile?</h2>
      <p>Tap your concern and we'll match you with the right treatment. Not sure? Book a consultation and we'll check for you.</p>
    </div>
    <div class="grid grid--4">{concerns}</div>
  </div>
</section>

<section class="section" id="results" aria-labelledby="results-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Before & After</span>
      <h2 id="results-title">Real Smile Transformations</h2>
      <p>Drag the slider to compare. Results like these are what our Iloilo patients come back to us for.</p>
    </div>
    <div class="grid grid--3">{ba}</div>
    <p class="disclaimer">Images are illustrations — replace with actual patient photos shared with written consent. Individual results vary.</p>
  </div>
</section>

<section class="section section--soft" id="credentials" aria-labelledby="cred-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Credentials</span>
      <h2 id="cred-title">Licensed, Accredited & Safe Dental Care</h2>
      <p>Your health is in qualified hands. Here's why patients across Iloilo trust {SITE["name"]}.</p>
    </div>
    <div class="grid grid--3">{cred_html}</div>
    <div class="table-wrap">
      <table class="license-table">
        <caption class="visually-hidden">Dentist licenses and memberships</caption>
        <thead><tr><th scope="col">Dentist</th><th scope="col">PRC License No.</th><th scope="col">Specialisation</th><th scope="col">Membership</th></tr></thead>
        <tbody>
          <tr><td>Dr. [DENTIST NAME], DMD</td><td>[PRC NO.]</td><td>General & Cosmetic Dentistry</td><td>Philippine Dental Association</td></tr>
          <tr><td>Dr. [DENTIST NAME], DMD</td><td>[PRC NO.]</td><td>Orthodontics</td><td>Philippine Dental Association</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="section" id="about" aria-labelledby="about-title">
  <div class="container grid grid--2" style="align-items:center">
    <div class="about__img"><img src="images/about.svg" alt="Treatment room at Dentist Pro dental clinic in Nabitasan, La Paz, Iloilo City" width="600" height="450" loading="lazy"></div>
    <div>
      <span class="eyebrow">About Us</span>
      <h2 id="about-title">A Neighbourhood Dental Clinic in La Paz, Iloilo</h2>
      <p>{SITE["name"]} was built on a simple idea: everyone in Iloilo deserves a dentist they can trust, close to home. From our clinic in
      Nabitasan, La Paz, we care for children, students, working professionals and seniors from every corner of Metro Iloilo.</p>
      <p>We take time to listen, explain your options in plain language, and give you a clear price before we start — so there are no surprises.</p>
      <ul class="checklist">
        <li>Modern equipment and digital dental X-rays</li>
        <li>Comfortable, air-conditioned clinic</li>
        <li>Family-friendly — from first baby teeth to dentures</li>
        <li>Transparent pricing and installment options</li>
      </ul>
      <div class="dentist">
        <img src="images/dentist-placeholder.svg" alt="Dr. [DENTIST NAME], dentist at Dentist Pro Iloilo City" width="80" height="80" loading="lazy">
        <div><h3>Dr. [DENTIST NAME], DMD</h3><p>Lead Dentist · PRC Lic. No. [PRC NO.]</p></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--soft" id="reviews" aria-labelledby="reviews-title">
  <div class="container">
    <div class="section__head"><span class="eyebrow">Patient Stories</span><h2 id="reviews-title">What Our Iloilo Patients Say</h2></div>
    <div class="grid grid--3">{quotes}</div>
  </div>
</section>

{booking_section("")}

<section class="section section--soft" id="areas" aria-labelledby="areas-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Areas We Serve</span>
      <h2 id="areas-title">Find a Dentist Near You in Metro Iloilo</h2>
      <p>Patients visit us from every district of Iloilo City and nearby towns. Choose your area for directions and local info.</p>
    </div>
    {areas_list("")}
  </div>
</section>

{contact_section()}

{faq_section(HOME_FAQS, "Dentist Near Me in Iloilo — Frequently Asked Questions")}

{cta_band("Ready for a Healthier, Brighter Smile?")}
</main>
'''
    return head(title, desc, "", "", schemas, keywords=keywords) + header("", True) + body + footer("")


def page_location(l):
    prefix = "../"
    full = loc_full(l)
    where = "in" if l["slug"] == "la-paz" else "near"
    title = f'Dentist Near Me in {full} | {SITE["name"]}'
    desc = (f'Looking for a dentist near me in {l["name"]}? {SITE["name"]} in Nabitasan, La Paz is {l["distance"]} away ({l["time"]}). '
            f'Cleaning, braces, extraction & more. Call {SITE["phone_display"]}.')
    path = f'locations/{l["slug"]}.html'
    faqs = l["faqs"] + [
        (f"What dental services are available for {l['name']} patients?",
         "Check-ups and cleaning, fillings, root canal, extractions, braces, teeth whitening, veneers, dentures, crowns, bridges, implants and pediatric dentistry."),
        (f"How do I book a dentist near {l['name']}?",
         f"Use the appointment form on this page or call/text {SITE['phone_display']}. We'll confirm your schedule by call or SMS."),
    ]
    schemas = [
        business_schema(area_served=[{"@type": "Place", "name": full}, {"@type": "City", "name": "Iloilo City"}]),
        breadcrumb_schema([("Home", f'{SITE["domain"]}/'), ("Areas We Serve", f'{SITE["domain"]}/#areas'),
                           (f'Dentist near {l["name"]}', f'{SITE["domain"]}/{path}')]),
        faq_schema(faqs),
    ]
    landmarks = "".join(f"<li>{escape(x)}</li>" for x in l["landmarks"])
    near = "".join(
        f'<li><a href="{LOC_BY_SLUG[s]["slug"]}.html">Dentist near {LOC_BY_SLUG[s]["name"]}</a></li>' for s in l["near"])
    intro = "".join(f"<p>{escape(p)}</p>" for p in l["intro"])

    body = f'''<main id="main">
<section class="hero" aria-labelledby="hero-title">
  <div class="container">
    <nav class="breadcrumbs" aria-label="Breadcrumb"><ol>
      <li><a href="{prefix}index.html">Home</a></li><li><a href="{prefix}index.html#areas">Areas We Serve</a></li><li aria-current="page">{escape(l["name"])}</li>
    </ol></nav>
  </div>
  <div class="container hero__grid">
    <div>
      <span class="eyebrow">Dentist Near Me · {escape(full)}</span>
      <h1 id="hero-title">Dentist {where.capitalize()} {escape(l["name"])}, {"Iloilo City" if l["kind"] == "district" else "Iloilo"}</h1>
      <p class="hero__lead">Trusted, gentle dental care for {escape(l["name"])} families at {SITE["name"]} — {escape(l["distance"])} from you
      ({escape(l["time"])}). Cleaning, fillings, braces, root canal, extractions, dentures and more.</p>
      <div class="hero__ctas">
        <a class="btn btn--primary" href="#book">{icon("calendar")}Book an Appointment</a>
        <a class="btn btn--ghost" href="tel:{SITE["phone_tel"]}">{icon("phone")}Call {SITE["phone_display"]}</a>
      </div>
      <ul class="hero__badges">
        <li>{icon("check")}PRC-licensed dentists</li>
        <li>{icon("check")}Open Saturdays</li>
        <li>{icon("check")}HMO & installment options</li>
      </ul>
    </div>
    <div class="hero__art">
      <img src="{prefix}images/hero.svg" alt="Dentist Pro, a dentist near {escape(full)}" width="600" height="520" fetchpriority="high">
      <div class="hero__card">{icon("pin")}<span><strong>{escape(l["time"].capitalize())}</strong>from {escape(l["name"])} to Nabitasan, La Paz</span></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="local-title">
  <div class="container grid grid--2">
    <div>
      <span class="eyebrow">Serving {escape(l["name"])}</span>
      <h2 id="local-title">Your Dental Clinic Near {escape(l["name"])}</h2>
      {intro}
      <div class="route"><h3>How to get here from {escape(l["name"])}</h3><p>{escape(l["route"])}</p></div>
    </div>
    <div>
      <div class="card">
        <h3>Near these {escape(l["name"])} landmarks</h3>
        <ul class="checklist">{landmarks}</ul>
        <h3>Why {escape(l["name"])} patients choose us</h3>
        <ul class="checklist">
          <li>PRC-licensed dentists and strict sterilization</li>
          <li>Clear price quote before treatment</li>
          <li>Same-day toothache slots when available</li>
          <li>Braces, dentures &amp; installment options</li>
        </ul>
        <a class="btn btn--brand" href="#book">{icon("calendar")}Book Your Visit</a>
      </div>
    </div>
  </div>
</section>

<section class="section section--soft" id="treatments" aria-labelledby="treatments-title">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Treatments</span>
      <h2 id="treatments-title">Dental Services for {escape(l["name"])} Patients</h2>
      <p>Everything you'd search for — teeth cleaning near me, braces near me, tooth extraction near me — available in one clinic.</p>
    </div>
    {treatment_cards()}
  </div>
</section>

{booking_section(prefix, l)}

{contact_section(l)}

{faq_section(faqs, f"Dentist Near {l['name']} — FAQs")}

<section class="section section--soft" aria-labelledby="nearby-title">
  <div class="container">
    <div class="section__head"><h2 id="nearby-title">Also Serving Nearby Areas</h2></div>
    <ul class="areas">{near}</ul>
    <p class="text-center mt-2"><a href="{prefix}index.html#areas">See all areas we serve →</a></p>
  </div>
</section>

{cta_band(f"Need a Dentist Near {l['name']}? We're Ready When You Are.")}
</main>
'''
    return (head(title, desc, path, prefix, schemas,
                 keywords=f'dentist near me {l["name"]}, dentist {full}, dental clinic near {l["name"]}, braces {l["name"]} Iloilo')
            + header(prefix, False) + body + footer(prefix))


def page_simple(fname, title, h1, text, robots):
    body = f'''<main id="main">
<section class="hero" aria-labelledby="hero-title" style="min-height:50vh">
  <div class="container text-center">
    <h1 id="hero-title">{escape(h1)}</h1>
    <p class="hero__lead" style="margin:0 auto">{escape(text)}</p>
    <div class="hero__ctas" style="justify-content:center">
      <a class="btn btn--primary" href="index.html">Back to Home</a>
      <a class="btn btn--ghost" href="tel:{SITE["phone_tel"]}">{icon("phone")}Call {SITE["phone_display"]}</a>
    </div>
  </div>
</section>
</main>
'''
    hdr = header("", False).replace('href="#book"', 'href="index.html#book"')
    return head(title, text, fname, "", robots=robots) + hdr + body + footer("")


def sitemap():
    today = date.today().isoformat()
    urls = [(f'{SITE["domain"]}/', "1.0")] + [(f'{SITE["domain"]}/locations/{l["slug"]}.html', "0.8") for l in LOCATIONS]
    entries = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>\n" for u, p in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n'


def main():
    (ROOT / "locations").mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(page_home(), encoding="utf-8")
    for l in LOCATIONS:
        (ROOT / "locations" / f'{l["slug"]}.html').write_text(page_location(l), encoding="utf-8")
    (ROOT / "thank-you.html").write_text(page_simple(
        "thank-you.html", f'Thank You | {SITE["name"]}', "Thank You! We Got Your Request",
        "Our team will call or text you shortly to confirm your appointment.", "noindex, follow"), encoding="utf-8")
    (ROOT / "404.html").write_text(page_simple(
        "404.html", f'Page Not Found | {SITE["name"]}', "Page Not Found",
        "Sorry, that page doesn't exist. Head back home or call us to book your visit.", "noindex, follow"), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE["domain"]}/sitemap.xml\n', encoding="utf-8")
    print(f"Built index.html + {len(LOCATIONS)} location pages")


if __name__ == "__main__":
    main()
