# Import Representatives Script
# Executes both insert_representatives.sql and insert_representatives_wayback.sql in the Docker database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Importing Representatives to Database" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker container is running
Write-Host "Checking if database container is running..." -ForegroundColor Yellow
$containerStatus = docker ps --filter "name=senate_db" --format "{{.Status}}"

if (-not $containerStatus) {
    Write-Host "Error: Database container 'senate_db' is not running." -ForegroundColor Red
    Write-Host "Please start the container with: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Database container is running" -ForegroundColor Green
Write-Host ""

# Function to execute SQL file
function Invoke-SqlFile {
    param(
        [string]$SqlFile,
        [string]$Description
    )
    
    Write-Host "Processing: $Description" -ForegroundColor Cyan
    Write-Host "  File: $SqlFile" -ForegroundColor Gray
    
    # Check if file exists
    if (-not (Test-Path $SqlFile)) {
        Write-Host "  [ERROR] File not found - $SqlFile" -ForegroundColor Red
        return $false
    }
    
    # Copy SQL file to container
    Write-Host "  -> Copying file to container..." -ForegroundColor Gray
    docker cp $SqlFile senate_db:/tmp/temp_import.sql | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Failed to copy file to container" -ForegroundColor Red
        return $false
    }
    
    # Execute SQL file
    Write-Host "  -> Executing SQL file..." -ForegroundColor Gray
    $output = docker exec -i senate_db psql -U senate_user -d senate_db -f /tmp/temp_import.sql 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Failed to execute SQL file" -ForegroundColor Red
        Write-Host "  Output:" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        return $false
    }
    
    # Check for errors in output
    $errorLines = $output | Select-String -Pattern "ERROR:"
    if ($errorLines) {
        Write-Host "  [WARNING] Warnings/Errors found:" -ForegroundColor Yellow
        $errorLines | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
    } else {
        Write-Host "  [OK] Successfully executed" -ForegroundColor Green
    }
    
    Write-Host ""
    return $true
}

# Execute insert_representatives.sql
$success1 = Invoke-SqlFile -SqlFile ".\insert_representatives.sql" -Description "Current Representatives (insert_representatives.sql)"

# Execute insert_representatives_wayback.sql
$success2 = Invoke-SqlFile -SqlFile ".\insert_representatives_wayback.sql" -Description "Historical Representatives (insert_representatives_wayback.sql)"

# Display summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Import Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($success1 -and $success2) {
    Write-Host "[OK] All imports completed successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Some imports failed. Please check the output above." -ForegroundColor Yellow
}

Write-Host ""

# Show representative count
Write-Host "Querying database for representative count..." -ForegroundColor Yellow
$count = docker exec -i senate_db psql -U senate_user -d senate_db -t -c "SELECT COUNT(*) FROM Representative;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Total Representatives in database: $($count.Trim())" -ForegroundColor Green
} else {
    Write-Host "Could not retrieve representative count" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
