Function Show-Tree
{
    param (
        [string]$path = ".",
        [int]$level = 0,
        [string[]]$excludeDirs = @('__pycache__', '.idea'),
        [string]$fileExtension = "*.py"
    )
    $indent = " " * $level
    # List directories excluding the specified ones
    Get-ChildItem -Path $path -Directory | Where-Object {
        $excludeDirs -notcontains $_.Name
    } | ForEach-Object {
        "$indent+ $( $_.Name )"
        Show-Tree -path $_.FullName -level ($level + 4) -excludeDirs $excludeDirs -fileExtension $fileExtension
    }
    # List .py files
    Get-ChildItem -Path $path -File | Where-Object {
        $_.Extension -eq ".py"
    } | ForEach-Object {
        "$indent    $_"
    }
}

Show-Tree | Out-File -FilePath "folder_structure.txt"
