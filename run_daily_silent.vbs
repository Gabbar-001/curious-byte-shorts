Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Youtube Shorts"
WshShell.Run "cmd /c run_daily.bat", 0, False
