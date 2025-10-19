# API Dashboard

Este repositório contém uma API Flask (`api.py`) que lê um banco Access (`dados.accdb`) e uma dashboard estática (`dashboard.html`) que consome a API.

Instruções rápidas:

1. Inicializar repositório git (se ainda não estiver inicializado):

   git init

2. Adicionar arquivos e commitar:

   git add .
   git commit -m "Initial commit"

3. Adicionar remote e subir (substitua a URL pelo seu repositório):

   git remote add origin <URL-DO-REPO>
   git branch -M main
   git push -u origin main

Observações:
- O banco Access (`dados.accdb`) está listado no `.gitignore`. Se precisar versionar um esquema/dump, exporte para CSV ou outro formato.
- Ajuste o IP/host da API no `dashboard.html` se você preferir fixar um host diferente.
