# Haiti — LawCodex

Legislation of the Republic of Haiti (République d'Haïti) as plain Markdown, in the original
French. Part of [LawCodex](https://github.com/LawCodex).

**Status: minimal.** Haiti has no official online legislation database. The official journal
*Le Moniteur* (Presses Nationales d'Haïti) is not freely available online. This repo has the
1987 Constitution and the laws, decrees and orders (arrêtés) that a government ministry
publishes as PDFs.

## What is covered

| Directory | Contents | Files |
|---|---|---|
| `constitution/` | Constitution de la République d'Haïti of 29 March 1987, original text | 1 |
| `constitution/historique/` | Earlier constitutions (1957, 1964, 1964 as amended), `status: repealed` | 3 |
| `lois/` | Laws (public finance, procurement, anti-corruption, special funds…) | 7 |
| `decrets/` | Decrees (organisation of the central administration, civil service statute, income tax, Cour supérieure des comptes…) | 9 |
| `arretes/` | Orders (arrêtés): public accounting regulations, civil service, minimum wage, procurement thresholds… | 14 |

Many of these PDFs are complete issues of *Le Moniteur*. The text of the whole issue is kept,
including its table of contents and any other acts published in the same issue. The
`published` field gives the publication date shown by the source.

### Sources

- **Direction Générale du Budget**, Ministère de l'Économie et des Finances, "Cadre
  réglementaire": https://budget.gouv.ht/cadre-reglementaire/Constitution, `/Lois`,
  `/Décrets`, `/Arrêtés` and `/Comptes Spéciaux`. The texts it lists under "Comptes Spéciaux"
  are filed under `lois/` or `decrets/` according to their type.
- **Parlement haïtien**: the 1987 Constitution as published at
  http://www.parlementhaitien.ht/telechargements/constitution.pdf. That site is offline, so the
  copy was retrieved from the Internet Archive (capture of 2011-06-17,
  https://web.archive.org/web/20110617022113/http://www.parlementhaitien.ht/telechargements/constitution.pdf).
  The Direction du Budget also publishes a copy of the 1987 text, which was skipped as a
  duplicate.

## What is not covered (gaps)

- **Consolidated (amended) Constitution.** The *Loi constitutionnelle* of 9 May 2011 amending
  the 1987 Constitution (published in *Le Moniteur* on 19 June 2012) is available from official
  sources only as scanned PDFs: budget.gouv.ht, and parlementhaitien.ht via the Internet
  Archive. These were not OCR'd. The constitution file here is therefore the **original 1987
  text** without the 2011/2012 amendments. Its front matter says so.
- **Codes.** The Civil Code, Penal Code (including the 2020 Penal Code decree), Code of Criminal
  Procedure, Labour Code, Commercial Code and so on are not published online by an official
  source and are not included.
- **Le Moniteur** in general, and all other laws and decrees.
- Scanned PDFs on budget.gouv.ht with no text layer (not OCR'd), 14 items:
  - 2011 constitutional amendment law;
  - decrees of 6 January 2016 (×3), 28 September 1987 and 5 May 1987;
  - arrêtés of 9 January 2019, 29 March 2017 (one of two copies), 23 March 2017,
    23 September 2015, 22 July 2015 and 25 May 2012;
  - laws of 20 August 1996 and 16 September 1966.
- Haitian Creole (Kreyòl) versions: the 1987 Constitution has an official Kreyòl version,
  but no official online copy was found.

## Political and constitutional context (neutral summary)

The 1987 Constitution, as amended in 2011/2012, remains the formal constitution. No regular
elections have been held since 2016. Since January 2023 no elected officials have held
national office: the terms of the last senators ended, and the presidency was vacant after
President Jovenel Moïse was assassinated in July 2021. The country has been governed under
transitional arrangements outside the constitutional framework. In April 2024 a Transitional
Presidential Council (Conseil présidentiel de transition) was installed alongside a Prime
Minister, with a mandate set to end on 7 February 2026. The transitional authorities set up a
process to draft a new constitution, presented as a draft (*avant-projet*) in 2025 for public
debate and a planned referendum, and announced plans for elections. As of retrieval, no new
constitution had been adopted. Readers should check current sources for later developments.
This repository takes no position on these matters.

## Format

One Markdown file per document with YAML front matter (`title`, `type`, `jurisdiction`,
`language`, `date`, `published`, `status`, `source`, `archived_copy` where applicable, `note`,
`retrieved`). Text was extracted with `pdftotext` (no OCR) and kept as extracted. TITRE /
CHAPITRE / SECTION lines become `##` headings and articles become `### Article N` headings.
Page numbers were removed.

## Licence / copyright

These are official texts of the Republic of Haiti, published by the State. This is not an
official publication. Consult *Le Moniteur* for authoritative text.

## Regenerate

```sh
pip install -r scripts/requirements.txt   # plus poppler-utils
python3 scripts/ht_fetch.py               # caches PDFs in ../_raw/ht/pdf, writes Markdown
```

Retrieved: 2026-10-13.
