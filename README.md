# MiniVault - Template

Dashboard de gestion de projet intégrant Notion, Google Drive, Gmail et GitHub.

## Quick Start - Nouveau Projet

### 1. Dupliquer le template

```bash
cp -r "/Users/mac/claude-code-backup/Template MiniVault" "/Users/mac/claude-code-backup/Mon Projet"
```

### 2. Lancer le setup

```bash
cd "/Users/mac/claude-code-backup/Mon Projet"
python3 setup-project.py "Mon Projet"
```

Le script crée automatiquement :
- Une page parent Notion avec le nom du projet
- 6 databases (Tasks, Goals, Metrics, Milestones, Documents, Feedback)
- Le fichier `.env.local` avec tous les credentials et IDs Notion

### 3. Installer et lancer

```bash
npm install
npm run dev
```

Ouvrir http://localhost:3000

---

## Databases Notion

| Database | Description |
|----------|-------------|
| **Tasks** | Gestion des tâches (Kanban) |
| **Goals** | Métriques de sortie (ventes, abonnés...) |
| **Metrics** | Métriques d'entrée (posts, interactions...) |
| **Milestones** | Jalons du projet |
| **Documents** | Liens vers documentation |
| **Feedback** | Retours utilisateurs |

---

## Configuration

Les credentials sont stockés dans `setup-project.py`. Pour les modifier :

```python
CONFIG = {
    "NOTION_TOKEN": "ton_token",
    "GOOGLE_CLIENT_ID": "...",
    # etc.
}
```

---

## Tech Stack

- **Next.js 14** (App Router)
- **NextAuth.js** (OAuth Google & GitHub)
- **Tailwind CSS** + **shadcn/ui**
- **Notion API**

---

## Structure

```
/app
  /api           # Routes API (auth, notion, drive, github)
  /auth          # Page de connexion
/components
  /dashboard     # Sections du dashboard
  /ui            # Composants shadcn/ui
/lib
  auth.ts        # Config NextAuth
  project-config.ts  # Config projet
```

---

## Déploiement Vercel

1. Push sur GitHub
2. Importer dans Vercel
3. Ajouter les variables d'environnement
4. Mettre à jour `NEXTAUTH_URL` avec l'URL Vercel
5. Mettre à jour les callback URLs OAuth (Google Console, GitHub)

---

## Troubleshooting

| Problème | Solution |
|----------|----------|
| Erreur "No access token" | Se connecter avec le bon provider (Google pour Drive, GitHub pour repos) |
| Erreur Notion API | Vérifier que l'intégration a accès à la database |
| Erreur OAuth callback | Vérifier les URLs de callback dans les settings OAuth |

Pour plus de détails, voir `CLAUDE.md`.
