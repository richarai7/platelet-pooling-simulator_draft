# Quick Start: Test Azure Digital Twins Integration

## 🚀 One-Command Testing

```bash
# Deploy everything to Azure
./deploy_azure.sh

# Test everything
./test_azure_deployment.sh
```

That's it! The scripts will:
- ✅ Create all Azure resources
- ✅ Deploy Function App
- ✅ Upload models
- ✅ Create twins
- ✅ Run simulation
- ✅ Verify twins updated

---

## 📋 Step-by-Step Instructions

### 1. Deploy to Azure (5 minutes)

```bash
# Make scripts executable (first time only)
chmod +x deploy_azure.sh test_azure_deployment.sh

# Run deployment
./deploy_azure.sh
```

**What happens:**
- Creates resource group: `platelet-rg`
- Creates Digital Twins instance
- Creates Function App
- Configures everything automatically
- Saves config to `azure_deployment_config.env`

### 2. Test Deployment (2 minutes)

```bash
# Load configuration
source azure_deployment_config.env

# Run tests
./test_azure_deployment.sh
```

**What it tests:**
- Azure login ✓
- Digital Twins instance ✓
- Models uploaded ✓
- Twins created ✓
- Simulation runs ✓
- Twins updated ✓

### 3. Test from UI (3 minutes)

```bash
# Terminal 1: Start API
source azure_deployment_config.env
cd api
uvicorn main:app --reload

# Terminal 2: Start UI
cd ui
npm install  # First time only
npm run dev

# Open browser: http://localhost:5173
# Click "Run Simulation"
```

### 4. Verify in Azure Portal (1 minute)

1. Go to https://portal.azure.com
2. Search for your Digital Twins instance
3. Click "Azure Digital Twins Explorer"
4. Run query: `SELECT * FROM digitaltwins`
5. See your updated twins! 🎉

---

## ✅ Expected Results

After running `./test_azure_deployment.sh`:

```
╔══════════════════════════════════════════════════════════════════════════╗
║                     TESTING COMPLETED!                                    ║
╚══════════════════════════════════════════════════════════════════════════╝

📊 Test Results Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Azure Login:              SUCCESS
✓ Digital Twins Instance:   SUCCESS
✓ DTDL Models:              2 models uploaded
✓ Device Twins:             11 twins created
✓ Simulation:               SUCCESS
✓ Twin Updates:             VERIFIED
```

---

## 🔍 Verification Commands

### Check twins created
```bash
source azure_deployment_config.env

az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT COUNT() FROM digitaltwins"
```

### View specific twin
```bash
az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge
```

### Query all devices
```bash
az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT * FROM digitaltwins WHERE IS_OF_MODEL('dtmi:platelet:Device;1')"
```

---

## 🎯 What Gets Tested

| Test | What's Checked | Expected Result |
|------|----------------|-----------------|
| 1. Azure Login | `az account show` | Logged in ✓ |
| 2. Digital Twins | Instance exists and running | Status: Succeeded ✓ |
| 3. DTDL Models | Models uploaded | 2 models ✓ |
| 4. Device Twins | Twins created | 11 twins ✓ |
| 5. Simulation | Run simulation | Completes successfully ✓ |
| 6. Twin Updates | Check properties | Values updated ✓ |
| 7. API Flow | UI → API → Azure | Integration works ✓ |

---

## 📁 Files Created

After running `./deploy_azure.sh`:

- `azure_deployment_config.env` - Configuration with all endpoints and names

Example content:
```bash
export AZURE_DIGITAL_TWINS_ENDPOINT=https://platelet-dt-XXXXX.api.eus.digitaltwins.azure.net
export DT_INSTANCE=platelet-dt-XXXXX
export AZURE_FUNCTION_ENDPOINT=https://platelet-func-XXXXX.azurewebsites.net/...
export FUNCTION_APP=platelet-func-XXXXX
export RESOURCE_GROUP=platelet-rg
export ENABLE_AZURE_INTEGRATION=true
```

---

## ⚠️ Troubleshooting

### Script fails at login
```bash
az login
```

### Can't find DT instance
```bash
az dt list
```

### Models not uploading
```bash
cd /path/to/repo
az dt model create --dt-name $DT_INSTANCE \
    --models azure_integration/dtdl_models/*.json
```

### Twins not updating
```bash
# Test direct update
az dt twin update --dt-name $DT_INSTANCE --twin-id centrifuge \
    --json-patch '[{"op":"replace","path":"/status","value":"Test"}]'
```

---

## 🧹 Clean Up (Delete Everything)

```bash
source azure_deployment_config.env
az group delete --name $RESOURCE_GROUP --yes
```

**Warning:** This deletes all resources and cannot be undone!

---

## 📖 Full Documentation

For complete details, see:
- **TESTING_GUIDE.md** - Complete testing documentation
- **UI_API_AZURE_INTEGRATION.md** - API integration guide
- **QUICK_SETUP_UI_API_AZURE.md** - Quick setup reference

---

## 💰 Cost

**Expected cost:** ~$5-10/month for POC with minimal usage

**Free tier includes:**
- Digital Twins: 1000 messages/month free
- Function App: 1M executions/month free

**To minimize costs:**
- Delete resources when not in use
- Use consumption plan for Function App

---

## ✅ Success Checklist

- [ ] `./deploy_azure.sh` completed successfully
- [ ] `./test_azure_deployment.sh` shows all tests passed
- [ ] Can see twins in Azure Portal
- [ ] Can run simulation from UI
- [ ] Twins update when simulation runs
- [ ] API integration working

---

**Need help?** See `TESTING_GUIDE.md` for detailed troubleshooting.

**Ready to test?** Run `./deploy_azure.sh` now! 🚀
