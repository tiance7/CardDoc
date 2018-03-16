@ECHO OFF
set TOOLSDIR=..\sixcube\tools\templatec
set TARGETDIR=D:\unityProject\XianCard\Assets\Scripts\Templates

svn up

@echo "Generate csharp template files begin"
del /s %TARGETDIR%\*.cs
python %TOOLSDIR%\template_to_csharp.py -i template -o %TARGETDIR%\
svn add %TARGETDIR%\*.cs --force
@echo "Generate csharp template files end."
pause