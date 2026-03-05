$port = 8000
Write-Host "Checking for process on port $port..."
$tcp = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($tcp) {
    $pid_num = $tcp.OwningProcess
    Write-Host "Found process with PID: $pid_num. Killing..."
    try {
        Stop-Process -Id $pid_num -Force -ErrorAction Stop
        Write-Host "Process killed."
    }
    catch {
        Write-Host "Failed to kill process. It might require Admin privileges or is already gone."
        Write-Host $_.Exception.Message
    }
}
else {
    Write-Host "No process found on port $port."
}

$backendPath = "c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai\apps\backend"
Write-Host "Starting backend in: $backendPath"
Set-Location -Path $backendPath
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
