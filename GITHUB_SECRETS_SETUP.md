# GitHub Secrets Setup for Deployment

## Required Secrets

To enable automatic deployment to AWS EC2, you need to configure these secrets in your GitHub repository:

### 1. Navigate to Repository Settings
- Go to your GitHub repository
- Click on **Settings** tab
- In the left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Required Secrets

#### EC2_SSH_KEY
```
Name: EC2_SSH_KEY
Value: [Your EC2 private key content]
```

**How to get this:**
1. On your local machine where you have the EC2 key pair:
```bash
cat ~/.ssh/your-ec2-key.pem
```
2. Copy the entire content including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`
3. Paste it as the value for `EC2_SSH_KEY`

#### EC2_USER
```
Name: EC2_USER
Value: ubuntu
```

#### EC2_HOST
```
Name: EC2_HOST
Value: 56.228.31.230
```
(Use your actual EC2 public IP address)

### 3. Alternative: Using Domain Name
Instead of IP address, you can use domain name:
```
Name: EC2_HOST
Value: api.c0r.ai
```

## Deployment Workflow

The deployment will trigger automatically when you:
1. Push to `main` branch
2. Manually trigger via GitHub Actions tab

## Testing the Setup

### 1. Local Test
Before pushing, test locally:
```bash
# Test SSH connection
ssh -i ~/.ssh/your-key.pem ubuntu@56.228.31.230

# Test if you can access the project directory
ls -la /home/ubuntu/c0r.ai/
```

### 2. Manual Deployment Test
You can manually trigger deployment:
1. Go to GitHub repository
2. Click **Actions** tab
3. Click **Deploy to AWS EC2** workflow
4. Click **Run workflow** button

## Troubleshooting

### Common Issues

1. **SSH Key Permission Denied**
   - Make sure the private key content is copied correctly
   - Ensure the key has proper format with newlines

2. **Host Key Verification Failed**
   - The workflow uses `StrictHostKeyChecking=no` to avoid this
   - If issues persist, add the host to known_hosts

3. **Project Directory Not Found**
   - Make sure the repository is cloned to `/home/ubuntu/c0r.ai/`
   - Update the path in `.github/workflows/deploy.yml` if different

### Checking Deployment Status

After deployment, verify:
```bash
# Check if services are running
curl https://api.c0r.ai/
curl https://ml.c0r.ai/
curl https://pay.c0r.ai/

# Check GitHub Actions logs for details
```

## Security Notes

- Never commit private keys to the repository
- Use GitHub Secrets for all sensitive information
- Regularly rotate SSH keys
- Monitor deployment logs for any security issues 