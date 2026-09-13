# V7 — tre piedi innestati direttamente in B03

## Geometria

Base composta da tre pezzi: **B01** anteriore corto e tozzo, **B04** posteriore sinistro, **B05** posteriore destro. Ciascuno ha un incastro doppio scorrevole indipendente nel nuovo **B03** blu. Stampare anche il B03 aggiornato: sostituisce la versione con una sola giunzione diagonale.

Ogni gamba posteriore misura **240 mm dal centro del raccordo alla punta lungo il percorso del braccio**. Non è la lunghezza rettilinea del singolo STL. Il tratto finale orizzontale è lungo circa 131,824 mm prima del terminale arrotondato; spessore 3,5 mm e larghezza 24 mm. Il piede davanti misura 60 × 45,95 × 21 mm, incastro incluso.

Larghezza della base assemblata 306,50 mm; gruppo superiore largo 170 mm; quota dei piani di appoggio 220 mm. La nuova base richiede una verifica fisica di stabilità con il proprio tablet; non è dichiarata una portata.

## Quantità e stampa

Nove moduli, una copia ciascuno. Le due gambe hanno sedi e battute speculari: usare entrambi i file distinti. Nessun perno.

| Sigla | Pezzo | Copie | Ingombro orientato X × Y × Z, mm |
|---|---|---:|---|
| B03 | Raccordo centrale blu | 1 | 145.95 × 51.9 × 98.0 |
| B01 | Piede anteriore corto | 1 | 60.0 × 45.95 × 21.0 |
| B04 | Gamba posteriore sinistra | 1 | 150.713 × 152.021 × 26.0 |
| B05 | Gamba posteriore destra | 1 | 150.713 × 152.021 × 26.0 |
| S01 | Schienale a Y | 1 | 141.9 × 33.488 × 170.0 |
| S02 | Schienale superiore posteriore | 1 | 122.883 × 83.461 × 170.0 |
| S03 | Appoggio superiore anteriore | 1 | 122.883 × 57.845 × 170.0 |
| A01 | Appoggio sinistro | 1 | 78.233 × 82.62 × 56.667 |
| A02 | Appoggio destro | 1 | 78.233 × 82.62 × 56.667 |

B01, B04 e B05 sono orientati piatti; gli altri moduli su un fianco. Le gambe occupano 150,713 × 152,021 mm sul piatto: con brim 3 mm arrivano a circa 158 mm, entro il margine massimo di 200 mm. Importare in millimetri al 100%, senza ridimensionare. Controllare supporti, sedi e punte sottili nello slicer.

## Incastri

Double Jigsaw con due lobi contrapposti, collo 4,3 mm, lobo Ø5,9 mm, profondità 5,95 mm; gioco per superficie 0,15 mm e gioco frontale 0,20 mm. Ogni giunto ha una battuta e resta smontabile nel verso opposto. Stampare prima una copia di ciascun provino A e B. Non forzare gli incastri con martelli.

## Montaggio

Destra e sinistra guardando dal lato tablet. Sostenere B03 finché i tre piedi non sono montati.

1. **Prepara B03**. Sostieni il raccordo centrale blu B03: riceve direttamente tutti e tre i piedi.
2. **Inserisci B01**. Allinea il piede anteriore corto alla sede davanti a B03. Scorri da destra verso sinistra fino alla battuta.
3. **Inserisci B04 sinistro**. Allinea la gamba posteriore sinistra alla sede dietro B03. Scorri da sinistra verso destra.
4. **Inserisci B05 destro**. Allinea la gamba posteriore destra alla seconda sede dietro B03. Scorri da destra verso sinistra. Ora appoggia la base sui tre piedi.
5. **Monta S01**. Inserisci la forcella blu in B03 da destra verso sinistra.
6. **Monta S02**. Inserisci il modulo superiore posteriore da destra verso sinistra.
7. **Monta S03**. Unisci il modulo giallo al vertice, da destra verso sinistra.
8. **Inserisci A01**. Inserisci l’appoggio sinistro da sinistra verso destra.
9. **Inserisci A02**. Inserisci l’appoggio destro da destra verso sinistra. Piani di contatto a 220 mm dal tavolo.

## File e verifica

pezzi_singoli contiene nove STL. tutti_i_pezzi_separati.stl è una disposizione di riferimento, non un solo piatto. supporto_assemblato.stl è il riferimento completo. supporto_22cm.blend contiene scene e colori. La guida offline include esploso, montaggio animato, controlli mouse e schermo intero.

Controlli digitali: 9 moduli chiusi; 36 coppie senza sovrapposizioni; 699 campioni di inserimento; 8 battute; 16 controlli dei lobi. Provini verificati in 9 posizioni. STL ricontrollati dopo l’esportazione. Nessun collaudo fisico eseguito.

## Apertura e rinforzo dei posteriori

Ogni gamba posteriore è aperta di altri 25° verso l’esterno rispetto alla versione precedente, con rotazione nel piano del tavolo attorno al centro dell’attacco. Il percorso dal centro alla punta rimane 240 mm. La radice passa da 25 a 30 mm di larghezza e da 21 a 26 mm di spessore; la curva bassa passa da 3,5 a 6 mm e si raccorda alle estremità da 3,5 mm. Le sedi in B03 conservano la direzione di scorrimento originaria.

## Gruppo arancione più verticale

La faccia principale passa da 22.34° a 12.34° rispetto alla verticale: correzione di 10°. S03/A01/A02 sono adattati mantenendo invariata la quota Z delle superfici, quindi i piani di appoggio rimangono orizzontali a 220 mm. Il raccordo S02 blu è deformato gradualmente verso la nuova posizione superiore. Usare insieme le nuove versioni di S02, S03, A01 e A02. I profili dei giunti seguono la nuova geometria. La taratura G015 usa pioli maggiorati e un gioco nominale residuo di 0,15 mm per lato; la deformazione superiore modifica leggermente il gioco misurato lungo la normale locale.

## Taratura G015 — applicata a tutta la V7

Tutti i pioli contrapposti delle otto giunzioni sono maggiorati di 0,15 mm sul profilo. Sedi invariate. Lobo nominale Ø5,9 mm e collo 4,3 mm; gioco residuo nominale 0,15 mm per lato. I due provini standard prove/provino_A_x1.stl e prove/provino_B_x1.stl usano la stessa taratura. Reimportare i nuovi STL nello slicer: i progetti già aperti non si aggiornano automaticamente. Prima di ristampare tutti i moduli, verificare la coppia nuova: il risultato fisico non è ancora confermato.

prove/tolleranze contiene copie esplicite G015 e una variante G010 più stretta, solo per confronto. G010 NON è applicata ai moduli del supporto.
