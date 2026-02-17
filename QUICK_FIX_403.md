# Quick Fix: 403 Error Loading 3D Model

## The Problem You Had

```
Failed to load resource: the server responded with a status of 403
(This request is not authorized to perform this operation using this permission.)
```

When trying to load `platelet_lab.gltf` from:
```
https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf
```

## Why This Happened

The storage container was created successfully, but **Azure Blob Storage requires TWO permission settings** for public access:

1. ❌ **Storage Account Level**: `allowBlobPublicAccess` was set to `false` (default)
2. ⚠️ **Container Level**: Even though you used `--public-access blob`, it doesn't work without #1

## The Solution

### Option 1: Quick Fix (Automated) ⚡

Run this script from the repository root:

```bash
./scripts/fix_blob_storage_permissions.sh
```

This script will:
- ✅ Enable blob public access on the storage account
- ✅ Set container permissions to public blob access
- ✅ Test the URL to verify it's accessible
- ✅ Show you the results

### Option 2: Manual Fix

```bash
# 1. Enable blob public access at storage account level
az storage account update \
  --name plateletmodels \
  --resource-group <your-resource-group> \
  --allow-blob-public-access true

# 2. Set container public access level
az storage container set-permission \
  --name models \
  --account-name plateletmodels \
  --public-access blob \
  --auth-mode login

# 3. Test access (should return HTTP 200 OK)
curl -I https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf
```

## Verify the Fix

After running the fix, test in your browser:

**Open this URL:**
```
https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf
```

**Expected result:** File downloads or displays

**If still getting 403:**
- Wait 30-60 seconds for permission propagation
- Clear your browser cache
- Check if you need to upload the blob first

## Upload Your 3D Model (If Not Uploaded Yet)

```bash
az storage blob upload \
  --account-name plateletmodels \
  --container-name models \
  --name platelet_lab.gltf \
  --file 3d_models/templates/platelet_lab_template.gltf \
  --auth-mode login
```

## What Changed in This Fix

I've added several resources to help you and future users:

### 1. Comprehensive Troubleshooting Guide
📄 `docs/FIX_BLOB_STORAGE_403.md`
- Detailed explanation of the issue
- Multiple solution approaches
- Common problems and fixes
- Security considerations
- Alternative solutions (CDN, SAS tokens)

### 2. Automated Fix Script
🔧 `scripts/fix_blob_storage_permissions.sh`
- One-command solution
- Automatic verification
- Clear status reporting
- Troubleshooting hints

### 3. Updated Documentation
📚 Updated files:
- `3d_models/README.md` - Step-by-step setup with fix
- `docs/3D_SCENES_STUDIO_SETUP.md` - 3D viewer troubleshooting
- `README.md` - Quick reference to fix script

## Next Steps

1. ✅ Run the fix script or manual commands above
2. ✅ Verify the URL is accessible in your browser
3. ✅ Reload Azure 3D Scenes Studio
4. ✅ Try loading the model again
5. ✅ Clear your browser cache if needed

## Still Having Issues?

See the detailed troubleshooting guide:
```bash
cat docs/FIX_BLOB_STORAGE_403.md
```

Or check for these common issues:
- Blob not uploaded yet → Upload using command above
- Firewall rules blocking access → Check storage account network settings
- Wrong resource group → Verify with `az storage account show --name plateletmodels`

## Key Takeaway

When creating Azure Blob Storage containers for public access, **ALWAYS** do both:
1. Enable `allowBlobPublicAccess` on the storage account
2. Set `--public-access blob` on the container

The container creation alone is not enough! 🚨
