@echo off
setlocal EnableDelayedExpansion
rem ============================================================
rem  pack-plugin.cmd - pack a DSH plugin into a tgz whose runtime
rem  dependencies are inlined (npm bundleDependencies).
rem
rem  Flow:
rem    1. optional build
rem    2. npm install --omit=dev --legacy-peer-deps   (only if node_modules is missing)
rem    3. npm pkg set bundleDependencies[0..n]=<dep>
rem    4. npm pack --ignore-scripts --pack-destination <out>
rem    5. restore the original package.json
rem
rem  Usage:
rem    cd <plugin folder>
rem    pack-plugin.cmd [dep1 dep2 ...] [options]
rem
rem  It packs the CURRENT folder (the one you cd'ed into) and drops the
rem  tgz into that same folder. Only an OFFLINE package is produced:
rem  runtime "dependencies" are inlined automatically, except the ones the
rem  host profile provides - anything listed in peerDependencies (react,
rem  @deepseek-ai/cordis, @deepseek-ai/dsh-*, ...) plus the @deepseek-ai/dsh*
rem  and @deepseek-ai/cordis packages themselves. A dependency that the host
rem  does NOT provide (e.g. @deepseek-ai/schemastery in 0.28.x, which is a
rem  plain dependency there) is still inlined. List deps to narrow the set.
rem
rem  Options:
rem    -Repo <dir>        pack this folder instead of the current one
rem    -Deps a,b,c        dependencies to inline (comma or space separated)
rem    -Out <dir>         output folder (default: the current folder)
rem    -Build             run "npm run build" before packing
rem    -NoInstall         never run npm install
rem    -ForceInstall      run npm install even if node_modules exists
rem    -NoRestore         keep bundleDependencies in package.json
rem
rem  Examples:
rem    cd C:\path\to\workspace\repos\dsh-mnemon
rem    pack-plugin.cmd
rem    pack-plugin.cmd ws yaml
rem    pack-plugin.cmd -Deps ws,yaml -Out D:\pkgs
rem ============================================================

set "REPO=%CD%"
set "DEPS="
set "OUT=%CD%"
set "DO_INSTALL=1"
set "DO_FORCE_INSTALL=0"
set "DO_RESTORE=1"
set "DO_BUILD=0"

:parse
if "%~1"=="" goto parsed
if /i "%~1"=="-Repo"       ( set "REPO=%~2" & shift & shift & goto parse )
if /i "%~1"=="-Out"        ( set "OUT=%~2" & shift & shift & goto parse )
if /i "%~1"=="-Deps"       ( set "DEPS=%DEPS% %~2" & shift & shift & goto parse )
if /i "%~1"=="-Build"      ( set "DO_BUILD=1" & shift & goto parse )
if /i "%~1"=="-NoInstall"  ( set "DO_INSTALL=0" & shift & goto parse )
if /i "%~1"=="-ForceInstall" ( set "DO_FORCE_INSTALL=1" & shift & goto parse )
if /i "%~1"=="-NoRestore"  ( set "DO_RESTORE=0" & shift & goto parse )
if /i "%~1"=="-?"          goto usage
if /i "%~1"=="-h"          goto usage
if /i "%~1"=="--help"      goto usage
set "DEPS=%DEPS% %~1"
shift
goto parse
:parsed

if not defined REPO goto usage

for %%I in ("%REPO%") do set "REPO=%%~fI"
for %%I in ("%OUT%") do set "OUT=%%~fI"
if not exist "%OUT%" mkdir "%OUT%"
if not exist "%REPO%\package.json" (
    echo [!] "%REPO%" has no package.json - point -Repo at the plugin root.
    exit /b 1
)

set "NAME=|"
set "VERSION=|"
for /f "usebackq tokens=1,2 delims=|" %%a in (`node -e "const p=require(process.argv[1]);console.log(p.name+'|'+p.version)" "%REPO%\package.json"`) do (
    set "NAME=%%a"
    set "VERSION=%%b"
)
if "%NAME%"=="|" (
    echo [!] cannot read name/version from "%REPO%\package.json"
    exit /b 1
)

rem commas -> spaces so "-Deps a,b" and "a b" behave the same
if defined DEPS set "DEPS=%DEPS:,= %"
rem ---- default: inline every runtime dep the host does NOT provide ---------
rem  "host-provided" = declared in peerDependencies (react, react-dom,
rem  @deepseek-ai/cordis, every @deepseek-ai/dsh-*) plus the @deepseek-ai/dsh*
rem  and @deepseek-ai/cordis packages themselves. Everything else is inlined,
rem  including @deepseek-ai/schemastery when it is a plain dependency (0.28.x).
if not defined DEPS (
    for /f "usebackq delims=" %%D in (`node -e "const p=require(process.argv[1]);const host=Object.keys(p.peerDependencies||{}).concat(['@deepseek-ai/cordis']);console.log(Object.keys(p.dependencies||{}).filter(n=>host.indexOf(n)<0).filter(n=>n.indexOf('@deepseek-ai/dsh')<0).join(String.fromCharCode(32)))" "%REPO%\package.json"`) do set "DEPS=%%D"
)
if not defined DEPS echo     [!] package.json has no runtime dependencies to inline

echo.
echo ==^> %NAME% %VERSION%
echo     repo   %REPO%
echo     output %OUT%
echo     inline %DEPS%

if "%DO_BUILD%"=="1" (
    echo.
    echo ==^> build
    pushd "%REPO%"
    call npm run build --if-present
    if errorlevel 1 ( popd & echo [!] build failed & exit /b 1 )
    popd
)

if "%DO_INSTALL%"=="1" (
    if exist "%REPO%\node_modules" (
        if "%DO_FORCE_INSTALL%"=="0" (
            echo.
            echo ==^> node_modules exists, skip npm install ^(use -ForceInstall to redo^)
            goto install_done
        )
    )
    echo.
    echo ==^> npm install ^(runtime deps only^)
    pushd "%REPO%"
    rem --legacy-peer-deps: the plugin's peerOptional peers point at host
    rem packages (e.g. @huanlin/dsh-plugin-better-locale wants
    rem @deepseek-ai/dsh-client-locale ^0.1.0-rc.8 while the manifest pins
    rem 0.2.x); plain npm install dies with ERESOLVE before we can pack.
    call npm install --omit=dev --ignore-scripts --no-audit --no-fund --legacy-peer-deps
    if errorlevel 1 ( popd & echo [!] npm install failed & exit /b 1 )
    popd
)
:install_done

rem ---- bundleDependencies (always start from a clean manifest) ----------
echo.
echo ==^> bundleDependencies
copy /y "%REPO%\package.json" "%REPO%\package.json.packbak" >nul
if errorlevel 1 ( echo [!] cannot back up package.json & exit /b 1 )
pushd "%REPO%"
call npm pkg delete bundleDependencies >nul 2>nul
if defined DEPS (
    set "IDX=0"
    for %%D in (%DEPS%) do (
        call npm pkg set "bundleDependencies[!IDX!]=%%D" >nul
        if errorlevel 1 ( popd & echo [!] npm pkg set failed for %%D & exit /b 1 )
        echo     + %%D
        set /a IDX+=1
    )
)
popd
rem ---- pack -----------------------------------------------------------
echo.
echo ==^> npm pack
set "STAGE=%TEMP%\pack-plugin-stage"
if exist "%STAGE%" rmdir /s /q "%STAGE%" >nul 2>nul
mkdir "%STAGE%" >nul 2>nul
set "TGZ="
set "PACKLOG=%TEMP%\pack-plugin-npm-pack.log"
if exist "%PACKLOG%" del /q "%PACKLOG%" >nul 2>nul
pushd "%REPO%"
rem NOTE: do NOT capture npm's stdout with `for /f`. ERRORLEVEL after a
rem for/f loop is always 0, so a failed pack was never detected, and the
rem last stdout line is not reliably the tarball name (warnings can follow).
call npm pack --ignore-scripts --pack-destination "%STAGE%" > "%PACKLOG%" 2>&1
set "PACKRC=!ERRORLEVEL!"
popd
if not "!PACKRC!"=="0" goto fail_restore
rem Find the tarball npm actually wrote instead of parsing its output.
for %%F in ("!STAGE!\*.tgz") do set "TGZ=%%~fF"
if not defined TGZ goto fail_restore

rem ---- offline-installability check -----------------------------------
rem A plugin with runtime deps the host does not provide must inline them
rem (bundleDependencies + node_modules inside the tgz). A pure cordis-patch
rem plugin with no deps (e.g. @next-ai-drawio/dsh) needs no inlining - a
rem plain tgz of its files already installs offline.
if not defined DEPS goto no_inline
set "MF=%TEMP%\pack-plugin-manifest.json"
tar -xzOf "!TGZ!" package/package.json > "!MF!" 2>nul
if errorlevel 1 goto fail_restore
set "BCOUNT="
for /f "delims=" %%N in ('node -e "const p=require(process.argv[1]);console.log((p.bundleDependencies||p.bundledDependencies||[]).length)" "!MF!"') do set "BCOUNT=%%N"
if not defined BCOUNT goto fail_restore
if "!BCOUNT!"=="0" (
    echo [!] tarball has no bundleDependencies - it will NOT install offline
    goto fail_restore
)
tar -tzf "!TGZ!" 2>nul | findstr /i /c:"package/node_modules/" >nul
if errorlevel 1 (
    echo [!] tarball has no inlined node_modules - it will NOT install offline
    goto fail_restore
)
echo     verified !BCOUNT! bundled deps + inlined node_modules
goto restore
:no_inline
echo     no runtime deps to inline - tgz is offline-installable as-is

:restore
if exist "%REPO%\package.json.packbak" (
    if "%DO_RESTORE%"=="1" (
        move /y "%REPO%\package.json.packbak" "%REPO%\package.json" >nul
    ) else (
        del /q "%REPO%\package.json.packbak"
        echo     ! bundleDependencies kept in package.json
    )
)
if not exist "!TGZ!" exit /b 1

rem ---- move into the output folder -------------------------------------
rem Scoped names like @next-ai-drawio/dsh contain a slash - flatten it the
rem way npm does (@scope/pkg -> scope-pkg) so the filename is Windows-safe.
set "FINAL=%NAME%-%VERSION%-bundled.tgz"
set "FINAL=!FINAL:@=!"
set "FINAL=!FINAL:/=-!"
move /y "!TGZ!" "%OUT%\!FINAL!" >nul
if errorlevel 1 ( echo [!] cannot move tarball into %OUT% & exit /b 1 )
set "TGZ=%OUT%\!FINAL!"

rem ---- sanity check ----------------------------------------------------
tar -tzf "!TGZ!" >nul 2>nul
if errorlevel 1 (
    echo [!] tarball is broken: !TGZ!
    exit /b 1
)
goto report

:fail_restore
rem Restore the manifest but never move a failed or non-installable tarball.
if exist "%REPO%\package.json.packbak" (
    if "%DO_RESTORE%"=="1" (
        move /y "%REPO%\package.json.packbak" "%REPO%\package.json" >nul
    ) else (
        del /q "%REPO%\package.json.packbak"
    )
)
if exist "%PACKLOG%" type "%PACKLOG%"
echo [!] pack failed - no tarball was produced
exit /b 1

:report
rem ---- report ---------------------------------------------------------
for %%F in ("%TGZ%") do set "SIZE=%%~zF"
set "FILES=0"
for /f %%C in ('tar -tzf "%TGZ%" 2^>nul ^| find /c /v ""') do set "FILES=%%C"
set "SHA="
for /f "skip=1 delims=" %%H in ('certutil -hashfile "%TGZ%" SHA256') do (
    if not defined SHA set "SHA=%%H"
)
set "SHA=%SHA: =%"

echo.
echo ==^> done
echo     tarball %TGZ%
echo     size    %SIZE% bytes
echo     files   %FILES%
echo     sha256  %SHA%
echo.
echo   online install:
echo     dsh plugin --profile desktop add "%TGZ%"
if defined DEPS (
    echo   offline install:
    echo     install-plugin.cmd "%TGZ%"
)
exit /b 0

:usage
echo Usage: pack-plugin.cmd [dep1 dep2 ...] [options]
echo.
echo   cd into the plugin folder, then run pack-plugin.cmd. It packs the
echo   CURRENT folder and writes the offline tgz into that same folder.
echo   Runtime deps are inlined automatically (all "dependencies" except
echo   the ones the host profile provides: anything in peerDependencies,
echo   plus @deepseek-ai/dsh* and @deepseek-ai/cordis). List deps after the
echo   command to narrow the set.
echo.
echo   -Repo ^<dir^>      pack another folder instead of the current one
echo   -Deps a,b,c      inline these dependencies (comma or space separated,
echo                    same as listing them after the command)
echo   -Out ^<dir^>       output folder (default: current folder)
echo   -Build           run "npm run build" first
echo   -NoInstall       never run npm install
echo   -ForceInstall    reinstall even if node_modules exists
echo   -NoRestore       keep bundleDependencies in package.json
echo.
echo Examples:
echo   cd C:\path\to\workspace\repos\dsh-mnemon
echo   pack-plugin.cmd
echo   pack-plugin.cmd ws yaml
