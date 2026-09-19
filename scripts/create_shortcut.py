import os
import sys

def create_shortcut():
    import subprocess
    cmd = '''
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut("C:\\Dev\\projetos\\Claudin\\Anki\\Anki Flashcards.lnk")
    $Shortcut.TargetPath = "cmd.exe"
    $Shortcut.Arguments = '/c "C:\\Dev\\projetos\\Claudin\\Anki\\executar.bat"'
    $Shortcut.WorkingDirectory = "C:\\Dev\\projetos\\Claudin\\Anki"
    $Shortcut.Description = "Anki Flashcards Generator"
    $Shortcut.Save()
    '''
    ps_cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
    subprocess.run(ps_cmd, check=True)
    print("Atalho criado com sucesso em C:\\Dev\\projetos\\Claudin\\Anki\\Anki Flashcards.lnk")

if __name__ == "__main__":
    create_shortcut()
