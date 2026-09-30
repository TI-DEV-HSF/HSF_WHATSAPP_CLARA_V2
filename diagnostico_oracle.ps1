# Diagnóstico: Procurar Oracle Client instalado
Write-Host "`n🔍 DIAGNÓSTICO: Procurando Oracle Client..." -ForegroundColor Cyan

$paths_check = @(
    'C:\instantclient_19_23',
    'C:\instantclient_19_8',
    'C:\instantclient_21_3',
    'C:\instantclient_21_13',
    'C:\instantclient',
    'C:\oracle\instantclient',
    'C:\oracle\product\19.0.0\client_1\bin',
    'C:\oracle\product\21.0.0\client_1\bin',
    'C:\app\client\product\19.0.0\client_1\bin',
    'D:\instantclient',
    'W:\instantclient'
)

$encontrados = @()

foreach ($path in $paths_check) {
    if (Test-Path $path) {
        $oci_dll = Join-Path $path "oci.dll"
        if (Test-Path $oci_dll) {
            Write-Host "✅ ENCONTRADO: $path" -ForegroundColor Green
            $encontrados += $path
        }
    }
}

if ($encontrados.Count -eq 0) {
    Write-Host "`n❌ Nenhum Oracle Client encontrado!" -ForegroundColor Red
    Write-Host "`nVocê precisa:"
    Write-Host "  1. Instalar Oracle Instant Client"
    Write-Host "  2. Ou procurar onde está instalado (verifique em outro projeto)"
    Write-Host "  3. Adicionar o caminho em: config\.env"
} else {
    Write-Host "`n✅ Oracle Client disponível em: $($encontrados -join ', ')"
    Write-Host "`nUso: Adicione em config\.env conforme necessário"
}
