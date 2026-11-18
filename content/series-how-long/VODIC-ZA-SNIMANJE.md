# Serija "Koliko traje…?": vodič za snimanje nakon izlaska igre

Cilj: prvi video na internetu s **pravim, izmjerenim** vremenima iz igre.
Tvoj dio je snimanje i mjerenje. Video (karta, rute, mjerači, voditelj, glas, titlovi) radim ja automatski.

---

## Epizoda 1: "Koliko traje prijelaz cijele karte?"

### Prije snimanja
1. Otvori kartu u igri i izaberi **dvije krajnje točke**: najjužniju točku kopna i najsjeverniju (ili najzapadniju i najistočniju, što je duže).
2. Zapamti obje točke (marker na karti u igri) i drži se **iste rute** za sve tri vožnje.
3. Uključi štopericu na mobitelu. Vrijeme u igri ne vrijedi, mjerimo **stvarne minute**.

### Tri mjerenja
| # | Način | Kako | Što zapisati |
|---|---|---|---|
| 1 | **Pješice** | Sprint gdje može, bez auta i bez prečaca vodom | stvarne minute |
| 2 | **Autom** | Najbrži auto koji imaš, cestom, bez varanja | stvarne minute + koji auto |
| 3 | **Avionom / helikopterom** | Ravno od točke A do točke B | stvarne minute + koja letjelica |

Pješačenje može trajati jako dugo. Ako ti se ne da do kraja, izmjeri prvih 10 minuta i koliko si daleko stigao, a ja izračunam ukupno vrijeme. U videu tada piše "≈".

### Što snimiti (PS5: Create → *Save recent gameplay*; Xbox: Xbox tipka → *Capture*)
- **3–5 sekundi starta** svake vožnje (lik kreće, auto ubrzava, avion polijeće)
- **3–5 sekundi dolaska** na cilj
- **Snimku ekrana karte u igri** s označene obje točke. Po njoj radim **našu vlastitu stiliziranu kartu**, jer Rockstarovu ne smijemo samo kopirati.
- Po želji: smiješni momenti usput (pad s motora, policija…). Odlično su za kraj videa.

### Što mi poslati
Pošalji kroz `/submit` na Discordu (kategorija *Tip / mechanic*) ili mi direktno:
```
Epizoda: prijelaz karte
Start: [opis mjesta]  ·  Cilj: [opis mjesta]
Pješice: __ min
Autom: __ min  (auto: ______)
Avionom: __ min  (letjelica: ______)
+ klipovi i snimka karte
```

---

## Sljedeće epizode (isti format)
2. Koliko traje vožnja oko cijele obale?
3. Najbrži auto: koliko mu treba od grada do grada?
4. Koliko treba do najviše točke na karti?
5. Koliko dugo možeš bježati policiji s 5 zvjezdica?

---

## Kako nastaje video (moj dio, oko 10 minuta po epizodi)
1. Od tvoje snimke karte napravim našu stiliziranu kartu (jednom, vrijedi za sve epizode).
2. Upišem točke rute i vremena u `episode.json`.
3. Voditelj se bira nasumično (Scout, Nia, Mei ili Dev) i snima glas po predlošku ispod.
4. `python3 tools/route_video.py content/series-how-long/episode.json` napravi gotov video.
5. Dodam tvoje klipove starta i dolaska, pa zakažem objavu na sve kanale.

### Predložak teksta za voditelja (popunim tvojim brojkama)
> [confident] {Ime} here. [pause] How long does it take to cross the whole map? We actually timed it.
> On foot… {X} minutes. By car… {Y}. And by plane… just {Z}.
> [smug] Think you can beat that? Send us your time. Link in bio.
