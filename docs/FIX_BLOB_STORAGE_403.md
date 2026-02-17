# Fix: 403 Error Loading 3D Model from Azure Blob Storage

## Problem

When trying to load the 3D model (`platelet_lab.gltf`) from Azure Blob Storage in 3D Scenes Studio or a web application, you get a 403 error:

```
Failed to load resource: the server responded with a status of 403
(This request is not authorized to perform this operation using this permission.)
```

## Root Cause

The Azure Storage container was created but **does not have the correct public access level** configured. When you create a container, even with `--public-access blob`, the storage account itself may have additional security settings that prevent anonymous access.

## Solution

You need to:
1. Enable anonymous blob access on the storage account
2. Ensure the container has correct public access level
3. Verify the blob is publicly accessible

## Quick Fix (Command Line)

### Step 1: Enable Anonymous Blob Access on Storage Account

```bash
# Enable blob public access at the storage account level
az storage account update \
  --name plateletmodels \
  --resource-group <your-resource-group> \
  --allow-blob-public-access true
```

### Step 2: Set Container Public Access Level

```bash
# Update container to allow public blob access
az storage container set-permission \
  --name models \
  --account-name plateletmodels \
  --public-access blob \
  --auth-mode login
```

### Step 3: Verify Access

```bash
# Test if the blob is publicly accessible
curl -I https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf

# Should return: HTTP/1.1 200 OK
# NOT: HTTP/1.1 403 Forbidden
```

## Detailed Instructions

### Option A: Using Azure Portal

1. **Navigate to Storage Account**
   - Go to [Azure Portal](https://portal.azure.com)
   - Find your storage account: `plateletmodels`

2. **Enable Public Access**
   - Click on **Configuration** in the left menu
   - Find **"Allow Blob public access"**
   - Set to **Enabled**
   - Click **Save**

3. **Set Container Permissions**
   - Click on **Containers** in the left menu
   - Find container: `models`
   - Click the **...** (more options) button
   - Select **Change access level**
   - Set to **Blob (anonymous read access for blobs only)**
   - Click **OK**

4. **Verify**
   - Click on your container
   - Click on the blob: `platelet_lab.gltf`
   - Copy the URL
   - Open in a new browser tab
   - File should download (not show 403)

### Option B: Using Azure CLI

Run the automated script provided:

```bash
# From repository root
./scripts/fix_blob_storage_permissions.sh
```

Or manually:

```bash
# 1. Get your resource group name
RESOURCE_GROUP=$(az storage account show \
  --name plateletmodels \
  --query resourceGroup -o tsv)

echo "Resource Group: $RESOURCE_GROUP"

# 2. Enable blob public access at account level
az storage account update \
  --name plateletmodels \
  --resource-group $RESOURCE_GROUP \
  --allow-blob-public-access true

# 3. Wait a few seconds for propagation
sleep 5

# 4. Update container permissions
az storage container set-permission \
  --name models \
  --account-name plateletmodels \
  --public-access blob \
  --auth-mode login

# 5. Verify the blob is accessible
BLOB_URL="https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf"
echo "Testing access to: $BLOB_URL"
curl -I "$BLOB_URL"
```

## Verification Steps

### Test 1: Check Storage Account Setting

```bash
az storage account show \
  --name plateletmodels \
  --query allowBlobPublicAccess -o tsv

# Should return: true
```

### Test 2: Check Container Access Level

```bash
az storage container show \
  --name models \
  --account-name plateletmodels \
  --auth-mode login \
  --query properties.publicAccess -o tsv

# Should return: blob
```

### Test 3: Test Public Access

```bash
# Without authentication (public access)
curl -I https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf

# Should show: HTTP/1.1 200 OK
```

### Test 4: Load in Browser

Open this URL in your browser:
```
https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf
```

The file should download or display. If you see XML with "AuthenticationFailed" or "PublicAccessNotPermitted", the permissions are not set correctly.

## Common Issues

### Issue 1: "AllowBlobPublicAccess is set to false"

**Error Message:**
```
PublicAccessNotPermitted: Public access is not permitted on this storage account.
```

**Solution:**
```bash
az storage account update \
  --name plateletmodels \
  --resource-group <your-resource-group> \
  --allow-blob-public-access true
```

### Issue 2: Container Access Level is 'None'

**Error Message:**
```
403 Forbidden (no further details)
```

**Solution:**
```bash
az storage container set-permission \
  --name models \
  --account-name plateletmodels \
  --public-access blob \
  --auth-mode login
```

### Issue 3: Firewall Rules Blocking Access

**Error Message:**
```
403 Forbidden (intermittent)
```

**Solution:**
```bash
# Check firewall settings
az storage account show \
  --name plateletmodels \
  --query networkRuleSet

# Allow access from all networks (for public blob access)
az storage account update \
  --name plateletmodels \
  --resource-group <your-resource-group> \
  --default-action Allow
```

### Issue 4: Blob Not Uploaded Yet

**Error Message:**
```
404 Not Found
```

**Solution:**
```bash
# Upload the blob
az storage blob upload \
  --account-name plateletmodels \
  --container-name models \
  --name platelet_lab.gltf \
  --file 3d_models/templates/platelet_lab_template.gltf \
  --auth-mode login

# Or if template doesn't exist, you can upload any valid GLTF:
# az storage blob upload \
#   --account-name plateletmodels \
#   --container-name models \
#   --name platelet_lab.gltf \
#   --file /path/to/your/model.gltf \
#   --auth-mode login
```

## Security Considerations

### Public Access Trade-offs

**What you're enabling:**
- Anonymous read access to blobs in the `models` container
- Anyone with the URL can download the 3D model

**What's still protected:**
- Write/delete operations (require authentication)
- Other containers in the storage account
- Storage account management operations

### Best Practices

1. **Only enable public access on containers that need it**
   ```bash
   # Keep other containers private
   az storage container set-permission \
     --name private-data \
     --account-name plateletmodels \
     --public-access off
   ```

2. **Use SAS tokens for sensitive models** (if needed)
   ```bash
   # Generate a SAS token with expiration
   az storage blob generate-sas \
     --account-name plateletmodels \
     --container-name models \
     --name platelet_lab.gltf \
     --permissions r \
     --expiry 2026-12-31 \
     --https-only \
     --auth-mode login
   ```

3. **Monitor access logs**
   ```bash
   # Enable storage analytics
   az storage logging update \
     --account-name plateletmodels \
     --log rwd \
     --retention 30 \
     --services b
   ```

## Alternative Solutions

### Option 1: Use Azure CDN (Better Performance)

For production deployments:

```bash
# Create CDN profile
az cdn profile create \
  --name platelet-cdn \
  --resource-group <your-resource-group> \
  --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
  --name platelet-models \
  --profile-name platelet-cdn \
  --resource-group <your-resource-group> \
  --origin plateletmodels.blob.core.windows.net
```

### Option 2: Use Shared Access Signature (More Secure)

If you don't want fully public access:

```bash
# Generate long-lived SAS token
END_DATE=$(date -u -d "1 year" '+%Y-%m-%dT%H:%MZ')

SAS_TOKEN=$(az storage container generate-sas \
  --account-name plateletmodels \
  --name models \
  --permissions r \
  --expiry $END_DATE \
  --https-only \
  --auth-mode login \
  -o tsv)

# Use URL with SAS token
echo "https://plateletmodels.blob.core.windows.net/models/platelet_lab.gltf?${SAS_TOKEN}"
```

### Option 3: Use Azure 3D Scenes Studio Upload

Instead of referencing external URL:

1. In 3D Scenes Studio, choose **"Upload file"** instead of **"From URL"**
2. Upload the GLTF file directly (max 100MB)
3. Azure handles the storage and permissions automatically

## Next Steps

After fixing permissions:

1. ✅ **Verify blob is accessible** with curl/browser
2. ✅ **Reload 3D Scenes Studio** and try loading the model again
3. ✅ **Clear browser cache** if still seeing 403
4. ✅ **Test with simulation** to see real-time updates

## Reference

- [Azure Storage Anonymous Access](https://learn.microsoft.com/azure/storage/blobs/anonymous-read-access-configure)
- [Container Access Levels](https://learn.microsoft.com/azure/storage/blobs/anonymous-read-access-configure#set-the-public-access-level-for-a-container)
- [Storage Account Security](https://learn.microsoft.com/azure/storage/common/storage-security-guide)

## Support

If you continue to experience issues after following this guide:

1. Check Azure service health: https://status.azure.com
2. Review storage account diagnostics in Azure Portal
3. Contact Azure Support for account-specific issues
4. Open an issue in this repository with error details
