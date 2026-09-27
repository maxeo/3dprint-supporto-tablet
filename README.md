# Supporto per tablet

Supporto per tablet stampato in 3D (V7), in 9 pezzi a incastro senza perni.

**Guida di stampa e montaggio:** https://maxeo.github.io/3dprint-guide/supporto-tablet/guida.html

La guida online è una copia pubblica di [guida.html](guida.html), pubblicata dal repo
[3dprint-guide](https://github.com/maxeo/3dprint-guide).

## Contenuto

- `guida.html`, [documenti/ISTRUZIONI.md](documenti/ISTRUZIONI.md), `documenti/QUANTITA_DA_STAMPARE.txt`: istruzioni, geometria e quantità (misure in `dati/`)
- `stl/pezzi_singoli/`: STL dei 9 pezzi da stampare
- `stl/supporto_assemblato.stl`, `stl/tutti_i_pezzi_separati.stl`, `blender/supporto_22cm.blend`: modello completo
- `prove/`: provini degli incastri
- `originale/`: modello di partenza

## Varianti con meno pezzi

Nella guida il pulsante **Varianti** (in alto, accanto a Stampante) unisce moduli in un solo pezzo: vista 3D, passaggi, mappa e lista di stampa si aggiornano; la scelta resta salvata nel browser e si può condividere con `guida.html#variante=S04,B06`.

| Sigla | Unisce | Stampa X × Y × Z, mm | Note |
|---|---|---|---|
| A03 | S03 + A01 + A02 | 189,22 × 117,68 × 170 | supporto di circa 57 mm fra i due appoggi |
| S04 | S02 + S03 + A01 + A02 | 189,22 × 187,76 × 170 | come A03 |
| S05 | S01 + S02 + S03 + A01 + A02 | 252,88 × 187,76 × 170 | non entra in un piatto da 220–230 mm |
| B06 | B03 + B01 | 145,95 × 85,95 × 98 | sbalzo basso sotto il piede, circa 20 mm |

Parte alta e base si scelgono separatamente: da 9 pezzi si arriva a 4 (S05 + B06 + B04 + B05). I pezzi uniti conservano gli incastri esterni tarati (G015) e lo stesso orientamento di stampa dei moduli; gli incastri interni spariscono e il loro gioco è riempito.

Gli STL sono in `stl/varianti/` e le misure in `dati/varianti.json`, generati da `blender/varianti.py` (anche come testo nel `.blend`: Alt+P) o da riga di comando:

```
blender -b blender/supporto_22cm.blend --python blender/varianti.py
```

Lo script unisce i solidi V7 nella posa di montaggio e riempie le fessure dei giunti interni con l'intersezione dei due pezzi spostati di ±0,35 mm in 26 direzioni: niente sporgenze oltre le superfici esterne. Controllato: un solo solido chiuso per variante, ingombri uguali a quelli dei pezzi di partenza. Nessuna prova di stampa eseguita.

Nel `.blend` la scena **Montaggio** ha `Standard_9_pezzi` (Base, Schienale, Appoggio), `Varianti` (esclusa dalla vista: accendila nell'Outliner) e `Riferimento`; la scena **Stampa** ha i moduli orientati, i provini e `Varianti_stampa`.
