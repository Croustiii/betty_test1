# Projet : Client Python d'analyse de données Polymarket

## Objectif
Construire un client Python propre et modulaire pour interroger les API publiques 
de Polymarket à des fins de **lecture et d'analyse de données de marché** (pas de trading). 
Aucune authentification, clé ou wallet n'est nécessaire : on utilise uniquement les 
endpoints publics.

## Outillage et environnement
- **Gestionnaire de projet : `uv`**. Le projet doit être initialisé et géré entièrement 
  avec uv (pas de pip/venv manuel, pas de requirements.txt).
- **Python 3.14** (dernière version). Épingler la version via `uv python pin 3.14` et 
  `requires-python = ">=3.14"` dans le pyproject.toml.
- Initialiser avec `uv init` (structure packagée), ajouter les dépendances via 
  `uv add`, et lancer les scripts via `uv run`.
- Le README doit documenter les commandes uv (`uv sync`, `uv run ...`).

## APIs à utiliser (toutes publiques, REST, sans auth)
- **Gamma API** (`https://gamma-api.polymarket.com`) : découverte des marchés, events, 
  tags, recherche. API principale pour browser les données.
- **CLOB API publique** (`https://clob.polymarket.com`) : prix, midpoints, spreads, 
  carnets d'ordres, historique de prix. Requêtés PAR token_id.
- **Data API** (`https://data-api.polymarket.com`) : positions, trades, holders, activité 
  (à intégrer en option, pas prioritaire pour le MVP).

## Concepts métier à respecter dans le code
- **Event vs Market** : un event regroupe plusieurs markets. Modéliser les deux.
- **`condition_id`** : identifiant on-chain qui relie Gamma, CLOB et Data.
- **`token_id`** : chaque issue (Yes/No) a son propre token. Les prix et carnets se 
  requêtent par token_id, pas par market.
- Le **prix d'un token = probabilité implicite** (entre 0 et 1). Le commenter clairement.

## Architecture demandée (séparation en couches)
1. **Couche client HTTP** (`client/`) : appels bruts, avec :
   - gestion centralisée de l'URL de base par API
   - retry automatique avec backoff exponentiel
   - rate-limiting (petit délai entre appels + respect des 429)
   - timeout configurable
2. **Couche models** (`models/`) : parsing des réponses en modèles **Pydantic** 
   (Event, Market, Token, OrderBook, PricePoint...). Typage strict pour documenter 
   la structure et détecter les changements d'API.
3. **Couche analyse** (`analysis/`) : helpers pandas (charger des marchés en DataFrame, 
   calculer des stats, etc.).
4. **Config** (`config.py`) : URLs de base, limites de pagination, délais. Pas de secrets.

## Fonctionnalités du MVP
- `get_markets()` : récupère les marchés actifs avec **pagination complète** 
  (boucle limit/offset jusqu'à épuisement). Filtrage côté serveur (`active=true`, 
  `closed=false`).
- `get_market(condition_id)` : détail d'un marché + ses tokens.
- `get_price(token_id, side)` et `get_orderbook(token_id)` : via CLOB.
- `get_price_history(token_id)` : historique pour analyse.
- Un script d'exemple `examples/fetch_active_markets.py` qui liste les marchés actifs, 
  récupère leurs prix, et les charge dans un DataFrame pandas affiché proprement. 
  Lançable avec `uv run examples/fetch_active_markets.py`.

## Exigences techniques
- Python 3.14, géré via uv.
- Dépendances (ajoutées via `uv add`) : `httpx` (client HTTP, prévoir l'async pour 
  plus tard), `pydantic` v2, `pandas`. Optionnel : `tenacity` pour le retry.
- Dépendances de dev via `uv add --dev` : `ruff` (lint + format), `pytest`.
- **Cache disque** des réponses (SQLite ou fichiers Parquet) pour éviter de re-télécharger 
  lors de l'analyse historique.
- Type hints partout (profiter de la syntaxe moderne 3.14 : `X | None`, génériques natifs, 
  pas de `typing.Optional`/`List`). Docstrings sur les fonctions publiques.
- `pyproject.toml` propre (généré par uv), un `README.md` avec instructions uv.
- Gestion d'erreurs claire (erreurs réseau, 429, réponses malformées).
- Ne PAS sur-ingénierer : code lisible, pas de couches inutiles.

## Étapes
1. Vérifie que Python 3.14 est disponible (`uv python install 3.14` si besoin), puis 
   initialise le projet avec `uv init` et épingle la version.
2. Ajoute les dépendances via `uv add` / `uv add --dev`.
3. **Avant de figer les modèles Pydantic**, fais un appel test réel à Gamma `/markets` 
   et au CLOB pour vérifier la structure exacte des réponses, car la doc peut être 
   incomplète et les champs évoluent.
4. Construis les couches dans l'ordre : client → models → fonctions → exemple.
5. Lance le script d'exemple avec `uv run` pour valider le bout en bout, et `uv run ruff 
   check` pour le lint.

Commence par me proposer l'arborescence du projet, puis implémente.