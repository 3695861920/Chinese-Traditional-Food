$ErrorActionPreference = 'Continue'
$hosts = @('services.gradle.org', 'maven.neoforged.net', 'repo.maven.apache.org', 'libraries.minecraft.net')

foreach ($h in $hosts) {
    Write-Output ("=== " + $h)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($h, 443)
        $ssl = New-Object System.Net.Security.SslStream($tcp.GetStream(), $false, ({ $true }))
        $ssl.AuthenticateAsClient($h)
        $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($ssl.RemoteCertificate)
        Write-Output ("  subject : " + $cert.Subject)
        Write-Output ("  issuer  : " + $cert.Issuer)
        $chain = New-Object System.Security.Cryptography.X509Certificates.X509Chain
        $ok = $chain.Build($cert)
        Write-Output ("  chain   : " + $ok)
        foreach ($el in $chain.ChainElements) {
            Write-Output ("    - " + $el.Certificate.Subject)
        }
        $ssl.Dispose(); $tcp.Close()
    } catch {
        Write-Output ("  TLS ERROR: " + $_.Exception.Message)
    }
}

Write-Output ''
Write-Output '=== curl HEAD services.gradle.org'
& curl.exe -sS -o NUL -w "http_code=%{http_code} size=%{size_download}`n" --max-time 30 -I https://services.gradle.org/distributions/gradle-9.2.1-bin.zip

Write-Output ''
Write-Output '=== JAVA_TOOL_OPTIONS'
Write-Output ("  user  : " + [Environment]::GetEnvironmentVariable('JAVA_TOOL_OPTIONS', 'User'))
Write-Output ("  machine: " + [Environment]::GetEnvironmentVariable('JAVA_TOOL_OPTIONS', 'Machine'))
Write-Output ("  process: " + $env:JAVA_TOOL_OPTIONS)
