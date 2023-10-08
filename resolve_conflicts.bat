:resolve_conflicts
REM Check for unmerged paths
git status | findstr "Unmerged paths"
IF %ERRORLEVEL% NEQ 0 (
    echo All conflicts resolved.
    GOTO end
)

REM Get the list of conflicted files and accept changes from the new repository
for /f "tokens=*" %%f in ('git diff --name-only --diff-filter=U') do (
    git checkout --theirs "%%f"
)

REM Add resolved files and continue the rebase
git add .
git rebase --continue
IF %ERRORLEVEL% NEQ 0 (
    echo Rebase process completed or failed.
    GOTO end
)

REM Repeat until no more conflicts
GOTO resolve_conflicts

:end
echo Rebase process completed.