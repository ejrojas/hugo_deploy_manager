import os
import yaml
import ftplib
import subprocess
import logging
import argparse
from typing import Dict
from pathlib import Path

class HugoDeployer:
    def __init__(self, site_path: str, config_name: str = 'deploy_config.yaml'):
        self.site_path = site_path
        self.config_name = config_name
        self.config = self._load_config()
        self._setup_logging()

    def _load_config(self) -> Dict:
        config_path = os.path.join(self.site_path, self.config_name)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        log_dir = os.path.join(os.path.dirname(self.site_path), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join(log_dir, f'deploy_{self.config["site_name"]}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def deploy(self):
        try:
            self._build_site()
            self._upload_site()
            logging.info(f"Deployment completed for {self.config['site_name']}")
            print(f"✅ Successfully deployed {self.config['site_name']}")
        except Exception as e:
            error_msg = f"Deployment failed for {self.config['site_name']}: {str(e)}"
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            raise

    def _build_site(self):
        logging.info("Building site...")
        os.chdir(self.site_path)
        result = subprocess.run(['hugo', '--minify'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Hugo build failed: {result.stderr}")

    def _upload_site(self):
        logging.info("Starting FTP upload...")
        ftp = ftplib.FTP()
        ftp.connect(self.config['ftp']['host'], self.config['ftp']['port'])
        ftp.login(self.config['ftp']['user'], self.config['ftp']['password'])

        public_dir = os.path.join(self.site_path, 'public')
        for root, _, files in os.walk(public_dir):
            for fname in files:
                local_path = os.path.join(root, fname)
                remote_path = os.path.join(
                    self.config['ftp']['path'],
                    os.path.relpath(local_path, public_dir)
                )
                
                # Create remote directories if they don't exist
                remote_dir = os.path.dirname(remote_path)
                self._create_ftp_dirs(ftp, remote_dir)
                
                with open(local_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)
        
        ftp.quit()

    def _create_ftp_dirs(self, ftp: ftplib.FTP, path: str):
        """Create remote directories if they don't exist"""
        dirs = path.split('/')
        current = ''
        for d in dirs:
            if d:
                current += '/' + d
                try:
                    ftp.mkd(current)
                except ftplib.error_perm:
                    pass  # Directory probably exists

def load_global_config(config_path: str) -> Dict:
    """Load the global configuration file"""
    with open(config_path) as f:
        return yaml.safe_load(f)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Hugo site deployer')
    parser.add_argument(
        '--config', 
        default='sites_config.yaml',
        help='Path to global configuration file'
    )
    parser.add_argument(
        '--site', 
        help='Deploy specific site (must be listed in sites_config.yaml)'
    )
    parser.add_argument(
        '--list-sites', 
        action='store_true',
        help='List all configured sites'
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    try:
        # Find config file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, args.config)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Global config not found: {config_path}")

        config = load_global_config(config_path)
        base_path = os.path.expanduser(config.get('base_path', '.'))
        sites = config.get('sites', [])

        if args.list_sites:
            print("Configured sites:")
            for site in sites:
                print(f"- {site}")
            return

        if args.site:
            if args.site not in sites:
                print(f"Error: Site '{args.site}' not found in configuration")
                return
            sites = [args.site]

        for site in sites:
            site_path = os.path.join(base_path, site)
            deployer = HugoDeployer(site_path)
            deployer.deploy()

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()