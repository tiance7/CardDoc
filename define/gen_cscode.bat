@ECHO OFF
set TOOLSDIR=..\sixcube\tools\templatec
set TARGETDIR=%XIAN_CARD_PATH%\Assets\Scripts\Templates

rem svn up

@echo "Generate csharp template files begin"
del /s %TARGETDIR%\*.cs
python %TOOLSDIR%\template_to_csharp.py -i template -o %TARGETDIR%\
rem svn add %TARGETDIR%\*.cs --force
@echo "Generate csharp template files end."
pause