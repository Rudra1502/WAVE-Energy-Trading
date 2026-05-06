# Get all items in the current directory, ignoring the hidden .git folder
$items = Get-ChildItem -Path . -Exclude ".git", ".gitignore", "push_by_dir.ps1"

foreach ($item in $items) {
    # If the item is a folder
    if ($item.PSIsContainer) {
        Write-Host "Committing directory: $($item.Name)"
        git add "$($item.Name)"
        
        # Only commit if there are actually changes to commit
        $hasChanges = git status --porcelain "$($item.Name)"
        if ($hasChanges) {
            git commit -m "Implement $($item.Name) components"
            git push origin HEAD
        }
    } 
    # If the item is a standalone file
    else {
        Write-Host "Committing file: $($item.Name)"
        git add "$($item.Name)"
        
        $hasChanges = git status --porcelain "$($item.Name)"
        if ($hasChanges) {
            git commit -m "Add $($item.Name) configuration"
            git push origin HEAD
        }
    }
    Start-Sleep -Seconds 1
}

Write-Host "Finished pushing directory by directory!"
