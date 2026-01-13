# Guia completa de comandos Git

Guia rapida en ASCII con los comandos esenciales y avanzados para trabajar con Git, cada uno con una breve descripcion.

## Configuracion inicial (`git config`)
- `git config --global user.name "Tu Nombre"` : define el nombre de autor para todos tus repos.
- `git config --global user.email "tu@email.com"` : define el email de autor global.
- `git config --global core.editor "code --wait"` : usa VS Code como editor por defecto.
- `git config --list` : muestra la configuracion activa (global, local, sistema).

## Crear u obtener repositorios
- `git init [carpeta]` : inicializa un repo nuevo en la carpeta (crea si no existe).
- `git clone <url> [carpeta]` : copia un repo remoto a local (en carpeta opcional).
- `git clone --depth 1 <url>` : clon liviano solo con el ultimo snapshot.
- `git clone -b <rama> <url>` : clona solo una rama especifica.

## Estado y cambios basicos
- `git status -sb` : muestra estado resumido (staged, unstaged, untracked).
- `git diff` / `git diff --staged` / `git diff --stat` : diferencias en trabajo, staged o solo resumen.
- `git add <archivo>` / `git add .` / `git add -p` : lleva cambios al staging (archivo, todo o por hunks).
- `git commit -m "mensaje"` / `git commit -am "mensaje"` : crea commit (el -am incluye archivos ya trackeados).
- `git commit --amend [--no-edit]` : reescribe el ultimo commit (no usar tras push).
- `git show [hash]` : muestra detalle de un commit (por defecto el ultimo).

## Deshacer con cuidado
- `git restore <archivo>` : descarta cambios locales en un archivo.
- `git restore --staged <archivo>` : saca un archivo del staging (mantiene cambios locales).
- `git reset HEAD <archivo>` : version clasica para unstage.
- `git reset --soft HEAD~1` / `--mixed` / `--hard` : deshace ultimo commit dejando cambios en staging, en trabajo, o borrandolos (hard es destructivo).
- `git revert <hash>` : crea un commit inverso para deshacer de forma segura en historial compartido.

## Ramas y navegacion
- `git branch` / `git branch -a` / `git branch -vv` : lista ramas locales, todas, y tracking con ahead/behind.
- `git branch <nombre>` / `git branch -d <nombre>` / `-D` : crea o elimina rama (D fuerza aun sin merge).
- `git branch -m <viejo> <nuevo>` : renombra una rama.
- `git switch <rama>` / `git checkout <rama>` : cambia a otra rama.
- `git switch -c <rama>` / `git checkout -b <rama>` : crea y cambia a la nueva rama.
- `git checkout <hash>` : se mueve a un commit especifico (detached HEAD).

## Fusion y rebase
- `git merge <rama>` / `git merge --abort` : fusiona una rama en la actual o cancela el merge.
- `git merge --squash <rama>` : trae cambios pero los deja listos para un solo commit nuevo.
- `git rebase <rama-base>` : reescribe tus commits encima de otra base (historial lineal).
- `git rebase -i HEAD~N` : rebase interactivo (reordenar, squash, editar commits recientes).
- `git cherry-pick <hash>` : aplica un commit especifico sobre tu rama actual.

## Stash (guardar trabajo temporal)
- `git stash` / `git stash push -u -m "msg"` : guarda cambios actuales (con `-u` incluye no trackeados) con mensaje.
- `git stash list` : muestra los stashes guardados.
- `git stash show -p stash@{0}` : ve el diff guardado en un stash.
- `git stash pop` / `git stash apply` : aplica el stash (pop lo borra, apply lo conserva).
- `git stash drop stash@{0}` / `git stash clear` : borra un stash concreto o todos.

## Sincronizar con remotos
- `git remote -v` / `git remote add origin <url>` / `git remote set-url origin <url>` : lista, agrega o cambia el remoto.
- `git fetch origin` / `git fetch --all --prune` : trae refs nuevas (prune limpia ramas remotas eliminadas).
- `git remote prune origin` : borra referencias locales a ramas remotas que ya no existen.
- `git pull origin <rama>` / `git pull --rebase` : trae y fusiona, o trae y rebasea para historial lineal.
- `git push origin <rama>` / `git push -u origin <rama>` : sube la rama (con -u configura upstream).
- `git push --force-with-lease` : reescribe remoto de forma mas segura que `--force`.
- `git push origin :<rama>` : elimina una rama en el remoto.

## Historial e investigacion
- `git log --oneline --graph --decorate --all` : vista rapida de historial con ramas.
- `git log --stat` / `git log -p <archivo>` / `git log --author="Nombre"` : stats, diff de archivo, o filtro por autor.
- `git shortlog -sn` : cuenta de commits por autor.
- `git reflog` : historial de movimientos de HEAD (para recuperar estados pasados).
- `git blame <archivo>` : quien cambio cada linea y en que commit.

## Limpieza y otros
- `git clean -n` / `git clean -fd` : previsualiza o borra archivos/directorios no trackeados (usa -n primero).
- `git tag` / `git tag -a v1.0 -m "msg"` / `git push origin --tags` : lista, crea tags y los sube.
- `git bisect start` ... : busca el commit que introdujo un bug via busqueda binaria (`good` / `bad`).

## Comparar ramas rapidamente
- `git diff main..HEAD --stat` : resumen de tu rama actual contra main.
- `git diff main..feature --name-status` : lista de archivos tocados entre ramas.

