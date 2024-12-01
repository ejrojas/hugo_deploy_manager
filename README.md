# Hugo Deploy Manager

A lightweight Python utility for automated Hugo site deployments via FTP. Manage multiple Hugo sites with customizable configurations and scheduled deployments.

## Features
- Automated FTP deployment for Hugo sites
- Support for managing multiple sites
- Configurable deployment settings per site
- Detailed logging
- Command-line interface
- Scheduled deployment support

## Installation
Clone the repository:

```
git clone https://github.com/yourusername/hugo_deploy_manager.git
```

## Install required dependencies:

```
pip install pyyaml
```

## Configuration
The tool requires two configuration files:

### Global Configuration (sites_config.yaml)
This file defines the base path and list of sites to manage:

```
base_path: "/path/to/hugo/sites"
sites:
  - site1
  - site2
```

### Site-specific Configuration (deploy_config.yaml)
Each Hugo site needs a deploy_config.yaml in its root directory:

```
site_name: "my-site"
ftp:
  host: "ftp.example.com"
  user: "ftpuser"
  password: "password"
  path: "/public_html"
  port: 21
```

## Usage
### Basic Commands

Deploy all configured sites:
```
python deploy.py
```
List all configured sites:
```
python deploy.py --list-sites
```
Deploy a specific site:
```
python deploy.py --site site1
```
Use a custom configuration file:
```
python deploy.py --config custom_config.yaml
```

## Automated Deployment
To set up automated deployments using cron:

Open crontab:
```
crontab -e
```
Add a schedule (e.g., twice daily at 2 AM and 2 PM):
```
0 2,14 * * * cd /path/to/hugo_deploy_manager && python deploy.py
```

## Directory Structure
```
hugo_sites/
├── deploy_manager/
│   ├── deploy.py
│   ├── sites_config.yaml
│   └── requirements.txt
├── site1/
│   ├── deploy_config.yaml
│   └── [hugo site files]
└── site2/
    ├── deploy_config.yaml
    └── [hugo site files]
```

## Logging
Logs are stored in a logs directory at the base path. Each site has its own log file named deploy_[site_name].log.

## Security Considerations
- Keep FTP credentials secure.
- Add deploy_config.yaml to .gitignore.
- Set appropriate file permissions for configuration files.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
