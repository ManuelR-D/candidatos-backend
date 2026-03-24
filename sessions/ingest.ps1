# PowerShell script to ingest all session PDFs in the current folder to the API

param(
    [Parameter(Mandatory=$true)]
    [int]$Year,

    [Parameter(Mandatory=$false)]
    [int]$Amount = 0,
    
    [Parameter(Mandatory=$false)]
    [int]$TimeoutSeconds = 600,

    [Parameter(Mandatory=$false)]
    [bool]$DebugMode = $false,

    [Parameter(Mandatory=$false)]
    [bool]$Force = $false
)

Add-Type -AssemblyName System.Net.Http

# Configuration
$apiUrl = "http://localhost:5101/api/sessions/parse"
$debug = $DebugMode.ToString().ToLower()
$force = $Force.ToString().ToLower()

# Get all PDF files in the year subfolder
$yearFolder = Join-Path $PSScriptRoot $Year.ToString()
if (-not (Test-Path $yearFolder)) {
    Write-Host "Folder not found: $yearFolder" -ForegroundColor Red
    exit 1
}
$pdfFiles = Get-ChildItem -Path $yearFolder -Filter "*.pdf"

# Limit files if Amount parameter is specified
if ($Amount -gt 0) {
    $pdfFiles = $pdfFiles | Select-Object -First $Amount
    Write-Host "Limiting to first $Amount file(s)" -ForegroundColor Cyan
}

if ($pdfFiles.Count -eq 0) {
    Write-Host "No PDF files found in the $Year folder." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($pdfFiles.Count) PDF file(s) to process" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failureCount = 0
$skippedCount = 0
$results = @()

foreach ($pdfFile in $pdfFiles) {
    Write-Host "Processing: $($pdfFile.Name)" -ForegroundColor White
    
    try {
        # Create HTTP client with timeout
        $client = New-Object System.Net.Http.HttpClient
        $client.Timeout = New-TimeSpan -Seconds $TimeoutSeconds
        $content = New-Object System.Net.Http.MultipartFormDataContent
        
        # Add PDF file
        $fileStream = [System.IO.File]::OpenRead($pdfFile.FullName)
        $fileContent = New-Object System.Net.Http.StreamContent($fileStream)
        $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
        $content.Add($fileContent, "file", $pdfFile.Name)
        
        # Add debug parameter
        $debugContent = New-Object System.Net.Http.StringContent($debug)
        $content.Add($debugContent, "debug")
        
        # Add force parameter
        $forceContent = New-Object System.Net.Http.StringContent($force)
        $content.Add($forceContent, "force")
        
        # Send request
        $response = $client.PostAsync($apiUrl, $content).Result
        $result = $response.Content.ReadAsStringAsync().Result
        
        # Close file stream
        $fileStream.Close()
        $client.Dispose()
        
        # Parse response
        $jsonResponse = $null
        try {
            $jsonResponse = $result | ConvertFrom-Json
        } catch {
            Write-Host "  Status: Failed" -ForegroundColor Red
            Write-Host "  Error: Failed to parse response: $($_.Exception.Message)" -ForegroundColor Red
            $failureCount++
            $results += [PSCustomObject]@{
                File = $pdfFile.Name
                Status = "Failed"
                Error = "Invalid JSON response: $result"
            }
            continue
        }
        
        if ($response.IsSuccessStatusCode) {
            if ($jsonResponse -and $jsonResponse.already_parsed -eq $true) {
                Write-Host "  Status: Already Parsed (skipped)" -ForegroundColor Yellow
                $skippedCount++
                $results += [PSCustomObject]@{
                    File = $pdfFile.Name
                    Status = "Skipped"
                    SessionId = $jsonResponse.data.session_id
                    Message = $jsonResponse.message
                }
            } else {
                Write-Host "  Status: Success" -ForegroundColor Green
                Write-Host "  Session ID: $($jsonResponse.data.session_id)" -ForegroundColor Gray
                Write-Host "  Topics: $($jsonResponse.data.topics_stored)" -ForegroundColor Gray
                Write-Host "  Interventions: $($jsonResponse.data.interventions_stored)" -ForegroundColor Gray
                $successCount++
                $results += [PSCustomObject]@{
                    File = $pdfFile.Name
                    Status = "Success"
                    SessionId = $jsonResponse.data.session_id
                    Topics = $jsonResponse.data.topics_stored
                    Interventions = $jsonResponse.data.interventions_stored
                }
            }
        } else {
            Write-Host "  Status: Failed" -ForegroundColor Red
            if ($jsonResponse -and $jsonResponse.error) {
                Write-Host "  Error: $($jsonResponse.error)" -ForegroundColor Red
                $errorMsg = $jsonResponse.error
            } else {
                Write-Host "  Error: Unknown error (Status: $($response.StatusCode))" -ForegroundColor Red
                $errorMsg = "HTTP $($response.StatusCode): $result"
            }
            $failureCount++
            $results += [PSCustomObject]@{
                File = $pdfFile.Name
                Status = "Failed"
                Error = $errorMsg
            }
        }
    }
    catch {
        Write-Host "  Status: Error" -ForegroundColor Red
        Write-Host "  Exception: $($_.Exception.Message)" -ForegroundColor Red
        $failureCount++
        $results += [PSCustomObject]@{
            File = $pdfFile.Name
            Status = "Error"
            Error = $_.Exception.Message
        }
    }
    
    Write-Host ""
}

# Summary
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Ingestion Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Total Files: $($pdfFiles.Count)" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Skipped (Already Parsed): $skippedCount" -ForegroundColor Yellow
Write-Host "Failed: $failureCount" -ForegroundColor Red
Write-Host ""

# Display detailed results table
if ($results.Count -gt 0) {
    Write-Host "Detailed Results:" -ForegroundColor Cyan
    $results | Format-Table -AutoSize
}

# Exit with appropriate code
if ($failureCount -eq 0) {
    exit 0
} else {
    exit 1
}
