If Not IsObject(application) Then
   Set SapGuiAuto  = GetObject("SAPGUI")
   Set application = SapGuiAuto.GetScriptingEngine
End If
If Not IsObject(connection) Then
   Set connection = application.Children(0)
End If
If Not IsObject(session) Then
   Set session    = connection.Children(0)
End If
If IsObject(WScript) Then
   WScript.ConnectObject session,     "on"
   WScript.ConnectObject application, "on"
End If
session.findById("wnd[0]").maximize
session.findById("wnd[0]/tbar[0]/okcd").text = "zfir0194"
session.findById("wnd[0]").sendVKey 0
session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "20231201"
session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "20231231"
session.findById("wnd[0]/usr/ctxtSO_KOSTL-LOW").text = "6800"
session.findById("wnd[0]/usr/ctxtSO_KOSTL-HIGH").text = "6899"
session.findById("wnd[0]/usr/ctxtSO_KOSTL-HIGH").setFocus
session.findById("wnd[0]/usr/ctxtSO_KOSTL-HIGH").caretPosition = 4
session.findById("wnd[0]").sendVKey 8
session.findById("wnd[0]/shellcont/shell/shellcont[1]/shell").pressToolbarContextButton "&MB_EXPORT"
session.findById("wnd[0]/shellcont/shell/shellcont[1]/shell").selectContextMenuItem "&PC"
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus
session.findById("wnd[1]/tbar[0]/btn[0]").press
session.findById("wnd[1]").sendVKey 4
session.findById("wnd[1]").sendVKey 4
session.findById("wnd[1]/tbar[0]/btn[0]").press
