# Chunmun Kamal — client revision design

Open `index.html` in a browser. No build step is required to use the website.

For an HTTP preview, run `python -m http.server 8080` in this directory and open http://localhost:8080.

## Included pages

- Homepage
- About Me
- 1:1 Coaching, with Foundation, Accelerator and Mastery pathways and FAQs
- Workplace Wellbeing
- Six case studies
- Blog, including the existing stress resilience article
- Contact
- Midlife Recharge Call booking, with the client's Calendly calendar

The design uses the client's palette, a black transparent logo sourced from the existing website, serif headings, simple body typography, navy banners, warm neutral backgrounds and responsive layouts. Photos are reused from the existing website. Website copy is now verbatim from the supplied 63-slide revision deck: it has not been shortened, paraphrased, or corrected. All six testimonials and all six case studies are included. Exact duplicate paragraphs are consolidated; different wording is retained. Professional association logos are not fabricated: none were provided in the deck.

All 63 slides and 478 extracted text blocks are accounted for. `CONTENT-AUDIT.md` maps each slide to its destination. `content-audit.json` records the original text and disposition of each paragraph. `DESIGN-AUDIT.md` documents the slide layouts and `deck-layout.json` records extracted shape positions and fills. Slides 1–5 are design instructions; visual placeholders, presentation labels and integration specifications are implemented rather than displayed as marketing copy. Document spelling and the duplicate “Case Study #5” numbering are preserved.

## Connections still needed for production

- Contact currently prepares an email using `mailto:`; it does not send or store submissions. Connect a backend or form service for automatic submission.
- The deck mentions a free quiz but supplies no destination or questions. Its button currently requests the quiz by email. Replace with the final quiz URL.
- Calendly and Google Fonts require an internet connection. Typography has local serif and sans-serif fallbacks. The booking page also provides a direct calendar link.
- The existing site's portrait is reused. Replace it if the client supplies another approved photo.
- No hosting deployment or edits to the live WordPress site have been performed.

## Files and validation

`styles.css` contains the responsive design; `script.js` handles mobile navigation and the contact email draft. `build.py` extracts the original PowerPoint when available, preserving authored line breaks, and regenerates the HTML. It falls back to `revisions.json` when the PowerPoint is unavailable and uses the saved full stress article in `blog-source.json`. Its content checks fail if any source block is unaccounted for or any website paragraph differs from the source text, apart from layout whitespace.

Responsive layouts use fluid headings and spacing, readable tablet grids, stacked phone layouts and a mobile menu through 1024px. The menu resets when crossing between mobile and desktop layouts. Buttons and mobile navigation links have touch-friendly target sizes.

Browser checks covered all eight pages at 18 viewport widths from 320px to 2560px, including both sides of layout breakpoints: 144 page/width combinations, with no horizontal overflow or content extending outside the viewport. Mobile navigation, desktop/mobile resizing, Escape dismissal, FAQ expansion and workplace programme selection were exercised. Screenshots are in `preview/`, including tablet and phone previews. Third-party Calendly loading was excluded from this layout sweep; booking completion and actual email delivery were not tested.

Reference layouts reviewed: https://www.heidiallsopcoaching.com/, https://andreagiles.com/, https://susanfilan.com/. Existing assets and stress article sourced from https://chunmunkamal.web-testlink.com/.
