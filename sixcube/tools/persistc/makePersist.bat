@ECHO OFF
python daoXml2Cpp.py defines
copy /Y DaoTypes.h ..\server\library\das
python genPersistMain.py
PAUSE