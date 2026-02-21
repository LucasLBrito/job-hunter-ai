$port = 3000
Write-Host "Checking for process on port $port..."
$tcp = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($tcp) {
    # tcp can be an array. Iterate.
    foreach ($conn in $tcp) {
        $pid_num = $conn.OwningProcess
        if ($pid_num -eq 0) { continue }
        
        Write-Host "Found process with PID: $pid_num. Killing..."
        try {
            Stop-Process -Id $pid_num -Force -ErrorAction Stop
            Write-Host "Process $pid_num killed."
        } catch {
            Write-Host "Failed to kill process $pid_num : $($_.Exception.Message)"
        }
    }
} else {
    Write-Host "No process found on port $port."
}

Start-Sleep -Seconds 2

$frontendPath = "c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai\apps\frontend"
Write-Host "Starting frontend in: $frontendPath"
Set-Location -Path $frontendPath

# Use -- --port 3000 just in case, but default is 3000
npm run dev
