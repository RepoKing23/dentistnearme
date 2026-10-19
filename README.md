# Dentist Pro — Dentist Near Me, Iloilo City

A fast static website for **Dentist Pro**, Nabitasan, La Paz, Iloilo City (0993 495 3526). It is built to rank for "dentist near me" and other local searches in Metro Iloilo.

- `index.html`: the homepage. It has Call and Book buttons in the header, a hero, treatments, concerns, before & after sliders, credentials, about us, reviews, the booking form, areas served, a map and hours, and an FAQ.
- `locations/*.html`: 12 location pages: **La Paz, Jaro, Mandurriao, Molo, Arevalo, City Proper, Lapuz, Pavia, Oton, Leganes, Santa Barbara, San Miguel**.
- SEO: every page has its own title and description, a canonical link, geo meta tags, Open Graph tags, and `Dentist`, `FAQPage` and `BreadcrumbList` structured data (JSON-LD). The site also has `sitemap.xml` and `robots.txt`.
- No framework and no build step for hosting. The only JavaScript is `js/main.js`, which is small.

## Editing

Content, clinic details, treatments and locations are all in **`scripts/build.py`**. Edit them there, then rebuild:

```bash
python3 scripts/build.py
```

This rewrites `index.html`, `locations/`, `thank-you.html`, `404.html`, `sitemap.xml` and `robots.txt`. Don't edit those files directly, because the next build overwrites them. Styles are in `css/styles.css`.

## Replace these placeholders before going live

Edit these in the `SITE` block in `scripts/build.py`:

| Item | Where |
|---|---|
| Domain (`https://www.dentistpro-iloilo.com`) | `SITE["domain"]` (used in canonicals, the sitemap and structured data) |
| Clinic hours | `SITE["hours"]` |
| Exact map coordinates | `SITE["lat"]`, `SITE["lng"]`: right-click your clinic in Google Maps to copy them |
| Formspree form ID | `SITE["formspree"]` (see below) |

The site has no placeholder text. These sections were left out on purpose and can be added back to `page_home()` in `build.py` once you have the details:

- Dentist names and PRC license numbers (in the credentials and about-us sections).
- Patient reviews: use real Google reviews only.
- Your list of accepted HMOs and your certificates (in the credential cards).

Also replace these files in `images/`:

- `case-*-before.svg` and `case-*-after.svg`: real before & after photos, used **only with the patient's written consent**.
- `og-image.png`: the image shown when the site is shared on social media (1200×630).

The hero, clinic and banner photos are Unsplash stock photos, set in the `PHOTOS` block of `scripts/build.py`. They load straight from Unsplash's image servers, which Unsplash's rules require, and the photographers are credited in the footer. Swap them for real photos of your clinic and team when you have them: real photos build more trust and help local SEO.

## Appointment form

- **Netlify:** this works out of the box. Submissions appear under *Forms* in the Netlify dashboard, and you can turn on email notifications there.
- **Formspree (any host):**
  1. Create a form at formspree.io.
  2. Set `SITE["formspree"] = "https://formspree.io/f/<id>"`.
  3. Rebuild.

  The script sends to Formspree automatically once the placeholder ID is gone.

## Deploy

- **Netlify:** drag and drop this folder, or connect the repo. `netlify.toml` is included, and the publish directory is the repo root.
- **GitHub Pages:** go to Settings → Pages and deploy from this branch, using the root folder.

## Local SEO checklist after launch

1. Create or claim the **Google Business Profile**. Use exactly the same name, address and phone number as the site, and the category "Dentist".
2. Submit `sitemap.xml` in Google Search Console.
3. Ask happy patients for Google reviews. Reviews are a big factor in "near me" rankings.
4. List the clinic in Philippine directories (Facebook, Yellow Pages PH, etc.) with the same name, address and phone number.
5. Add real photos and update the location pages with local details over time.
