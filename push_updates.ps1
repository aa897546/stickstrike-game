$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/aa897546/stickstrike-game.git"
$branch = "addfuntion"
$files = @("main.py", "requirements.txt", "README-PYGAME.md", ".gitignore", "push_updates.ps1")

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
$bundledGit = "C:\Users\au604\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"

if ($gitCommand) {
    $git = $gitCommand.Source
} elseif (Test-Path $bundledGit) {
    $git = $bundledGit
    $gitRoot = Split-Path (Split-Path $bundledGit -Parent) -Parent
    $env:GIT_EXEC_PATH = Join-Path $gitRoot "mingw64\bin"
    $env:PATH = "$(Join-Path $gitRoot 'mingw64\bin');$(Join-Path $gitRoot 'cmd');$env:PATH"
} else {
    throw "Git could not be found. Install Git for Windows from https://git-scm.com/download/win"
}

$gitArgs = @("--git-dir=.push-git", "--work-tree=.")

if (-not (Test-Path ".push-git\HEAD")) {
    & $git @gitArgs init -b main
    & $git @gitArgs config user.name "Codex"
    & $git @gitArgs config user.email "codex@openai.com"
}

$remotes = & $git @gitArgs remote
if ($remotes -notcontains "origin") {
    & $git @gitArgs remote add origin $repoUrl
} else {
    $origin = & $git @gitArgs remote get-url origin
    if ($origin -ne $repoUrl) {
        & $git @gitArgs remote set-url origin $repoUrl
    }
}

$currentBranch = & $git @gitArgs branch --show-current
if ($currentBranch -ne $branch) {
    $remoteBranch = & $git @gitArgs ls-remote --heads origin $branch
    if ($remoteBranch) {
        & $git @gitArgs fetch origin $branch
        & $git @gitArgs switch -C $branch "origin/$branch"
    } else {
        & $git @gitArgs switch -C $branch
    }
}

& $git @gitArgs add -- $files
& $git @gitArgs diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    & $git @gitArgs commit -m "Update STICKSTRIKE ($timestamp)"
} else {
    Write-Host "No Pygame changes to commit."
}

& $git @gitArgs push -u origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "GitHub push failed. Check the network connection and run gh auth setup-git before retrying."
}

$headSha = & $git @gitArgs rev-parse HEAD
& $git @gitArgs branch -f main $headSha
& $git @gitArgs push -u origin main
if ($LASTEXITCODE -ne 0) {
    throw "The addfuntion branch was pushed, but the main branch push failed."
}

Write-Host "Updated addfuntion and main: https://github.com/aa897546/stickstrike-game"
